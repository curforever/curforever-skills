#!/usr/bin/env python3
"""Local, advisory multi-agent task records. No model/API/network calls."""
import argparse
import contextlib
import datetime
import os
if os.name == "nt":
    import msvcrt
else:
    import fcntl
import fnmatch
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import uuid

SCHEMA = 1
MAX_FILES = 10000
MAX_BYTES = 16 * 1024 * 1024
STATES = {"planned", "running", "paused", "blocked", "awaiting_review",
          "changes_requested", "accepted", "completed"}


class Conflict(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Conflict(message)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def identity(prefix):
    return prefix + "-" + uuid.uuid4().hex[:12]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def head(root):
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def canonical(path):
    p = Path(path).expanduser().resolve()
    need(p.is_dir(), "workspace must be an existing directory")
    try:
        r = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return Path(r.stdout.strip()).resolve()
    except (OSError, subprocess.TimeoutExpired):
        pass
    for parent in (p, *p.parents):
        if (parent / ".ai-cowork" / "project.json").is_file():
            return parent
    return p


def safe(path, base):
    """Keep owned metadata local and reject symlinks, including dangling ones."""
    p = Path(os.path.abspath(path))
    b = Path(os.path.abspath(base))
    try:
        rel = p.relative_to(b)
    except ValueError:
        raise Conflict("metadata path escapes its root")
    cur = b
    need(not cur.is_symlink(), "symlink metadata root refused")
    for part in rel.parts:
        cur = cur / part
        need(not cur.is_symlink(), "symlink metadata refused: " + str(cur))
    return p


def load(path, base):
    p = safe(path, base)
    need(p.is_file(), "missing record: " + str(p))
    need(p.stat().st_size <= MAX_BYTES, "record exceeds size limit")
    try:
        value = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        raise Conflict("corrupt JSON: " + str(p))
    need(isinstance(value, dict), "record must be an object")
    return value


def atomic(path, value, base):
    p = safe(path, base)
    p.parent.mkdir(parents=True, exist_ok=True)
    safe(p, base)
    fd, tmp = tempfile.mkstemp(prefix=".write-", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def immutable(path, text, base):
    p = safe(path, base)
    p.parent.mkdir(parents=True, exist_ok=True)
    safe(p, base)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as out:
        out.write(text)
        out.flush()
        os.fsync(out.fileno())


def textfile(path):
    p = Path(path).expanduser()
    need(p.is_file() and p.stat().st_size <= MAX_BYTES, "missing/oversized input document")
    value = p.read_text(encoding="utf-8")
    need(value.strip(), "empty input document")
    return value


@contextlib.contextmanager
def transaction(store, create=False):
    safe(store, store.parent)
    if create:
        store.mkdir(parents=True, exist_ok=True)
    need(store.is_dir(), "project not initialized; use init for a write request")
    lock = safe(store / ".transaction.lock", store)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        deadline = time.monotonic() + 3
        while True:
            try:
                if os.name == "nt":
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if exc.errno not in (11, 13, 35, 36):
                    raise
                need(time.monotonic() < deadline, "metadata busy; inspect before retry")
                time.sleep(0.05)
        yield
    finally:
        os.close(fd)  # Closing releases the OS lock on both platforms.


def scope_check(patterns):
    need(patterns and all(isinstance(p, str) and p.strip() for p in patterns), "scope required")
    for p in patterns:
        parts = Path(p).parts
        need(not Path(p).is_absolute() and ".." not in parts, "scope must be relative without ..")
        need(".git" not in parts and ".ai-cowork" not in parts, "scope cannot target owned/Git metadata")


def snapshot(workspace, patterns):
    scope_check(patterns)
    root = Path(workspace).resolve()
    files = {}
    def matches(parts, pattern, prefix=False):
        pats = tuple(x for x in pattern.split("/") if x not in {"", "."})
        @lru_cache(None)
        def walk(i, j):
            if j == len(pats):
                return True  # A matched directory includes its descendants.
            if i == len(parts):
                return prefix or all(x == "**" for x in pats[j:])
            if pats[j] == "**":
                return walk(i, j + 1) or walk(i + 1, j)
            return fnmatch.fnmatchcase(parts[i], pats[j]) and walk(i + 1, j + 1)
        return walk(0, 0)
    matched = set()
    count = 0
    for base, dirs, names in os.walk(root, followlinks=False):
        parent = Path(base)
        kept = []
        for name in dirs:
            q = parent / name
            parts = q.relative_to(root).parts
            if name in {".git", ".ai-cowork"}:
                continue
            if any(matches(parts, p, True) for p in patterns):
                if q.is_symlink():
                    files[str(q.relative_to(root))] = {"symlink": os.readlink(q)}
                else:
                    kept.append(name)
        dirs[:] = kept
        for name in names:
            q = parent / name
            rel = q.relative_to(root)
            if ".git" in rel.parts or ".ai-cowork" in rel.parts:
                continue
            selected = [p for p in patterns if matches(rel.parts, p)]
            if not selected:
                continue
            matched.update(selected)
            if q.is_symlink():
                files[str(rel)] = {"symlink": os.readlink(q)}
            elif q.is_file():
                need(q.stat().st_size <= MAX_BYTES, "scope contains oversized file; narrow scope")
                files[str(rel)] = hashlib.sha256(q.read_bytes()).hexdigest()
            else:
                raise Conflict("scope contains unsupported file type")
            count += 1
            need(count <= MAX_FILES, "scope too large; narrow scope")
    for p in patterns:
        if p not in matched:
            files["missing-pattern:" + p] = None
    return {"hash": digest({"scope": patterns, "files": files}), "files": files,
            "git_head": head(root), "at": now()}


def project(store, root):
    p = load(store / "project.json", store)
    need(p.get("schema") == SCHEMA and p.get("root") == str(root), "project identity/schema mismatch")
    return p


def find_task(store, ref):
    p = Path(ref).expanduser()
    if p.is_absolute():
        p = safe(p, store)
        need(p.parent.name == "tasks" and p.parent.parent.parent == store / "features",
             "task path is not a task record directory")
        return p
    need("/" not in ref and ref.startswith("task-"), "use exact task ID or absolute record directory")
    found = list((store / "features").glob("*/tasks/" + ref + "/state.json"))
    need(len(found) == 1, "task missing or ambiguous")
    return safe(found[0].parent, store)


def state_at(task, store):
    s = load(task / "state.json", store)
    need(s.get("schema") == SCHEMA and s.get("id") == task.name, "task identity/schema mismatch")
    need(s.get("status") in STATES and isinstance(s.get("version"), int), "invalid task status/version")
    need(isinstance(s.get("runs"), list) and isinstance(s.get("reviews"), list), "invalid task history")
    need(isinstance(s.get("workspace"), str) and isinstance(s.get("revision"), int), "invalid workspace/revision")
    scope_check(s.get("scope"))
    need(Path(s["workspace"]).resolve() == canonical(s["workspace"]), "workspace identity changed")
    plan = safe(task / "plans" / ("%04d.md" % s["revision"]), store)
    need(hashlib.sha256(plan.read_bytes()).hexdigest() == s.get("plan_hash"),
         "plan altered outside revise; restore exact version or reconcile explicitly")
    return s


def expected(s, a):
    need(s["version"] == a.expect_version, "stale state version; show and reconcile")


def save(task, s, store):
    s["version"] += 1
    s["updated_at"] = now()
    atomic(task / "state.json", s, store)


def lockpath(workspace):
    root = Path(workspace)
    return safe(root / ".ai-cowork" / "workspace.lock", root)


def acquire(workspace, owner):
    p = lockpath(workspace)
    safe(p.parent, Path(workspace))
    p.parent.mkdir(parents=True, exist_ok=True)
    owner["schema"] = SCHEMA
    owner.setdefault("operation", "execute")
    try:
        immutable(p, json.dumps(owner, ensure_ascii=False), Path(workspace))
    except FileExistsError:
        current = lock_record(workspace)
        raise Conflict("workspace occupied; owner=" + json.dumps(
            {k: current.get(k) for k in ("task", "run", "actor")}, ensure_ascii=False))


def lock_record(workspace):
    owner = load(lockpath(workspace), Path(workspace))
    need(owner.get("schema") == SCHEMA and owner.get("operation") in {"execute", "review"},
         "invalid workspace lock schema/operation; inspect without clearing")
    need(all(isinstance(owner.get(k), str) and owner[k].strip()
             for k in ("task", "run", "token", "actor")), "invalid workspace owner identity")
    return owner


def owned(workspace, task, run, token):
    owner = lock_record(workspace)
    need(owner.get("task") == str(task) and owner.get("run") == run and owner.get("token") == token,
         "workspace owner mismatch; refuse to clear or write")
    return owner


def release(workspace, task, run, token):
    owned(workspace, task, run, token)
    lockpath(workspace).unlink()


def active(s, a, task):
    expected(s, a)
    need(s["status"] == "running" and s.get("active_run"), "task is not running")
    r = next((r for r in s["runs"] if r["id"] == s["active_run"]), None)
    need(r is not None and r.get("token") == a.token and r["status"] == "running",
         "stale/wrong run token")
    need(r["revision"] == s["revision"], "run belongs to another plan")
    owned(s["workspace"], task, r["id"], a.token)
    return r


def public(s):
    value = json.loads(json.dumps(s))
    for r in value.get("runs", []):
        r.pop("token", None)
    return value


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def describe(task, s):
    result = public(s)
    result["task_path"] = str(task)
    result["plan_path"] = str(task / "plans" / ("%04d.md" % s["revision"]))
    result["evidence"] = snapshot(s["workspace"], s["scope"])["hash"]
    result["submitted_evidence"] = s["baseline"]["hash"]
    p = lockpath(s["workspace"])
    if p.exists() or p.is_symlink():
        owner = lock_record(s["workspace"])
        result["workspace_owner"] = {k: owner.get(k) for k in ("task", "run", "actor")}
    else:
        result["workspace_owner"] = None
    return result


def receipt(task, run, report, store, prefix="checkpoint"):
    target = task / "runs" / run / (identity(prefix) + ".md")
    immutable(target, report, store)
    return str(target)


def handoff(task, s, action, store):
    d = describe(task, s)
    plan = textfile(d["plan_path"])
    r = next((r for r in s["runs"] if r["id"] == s.get("last_run")), None)
    report = ""
    if r and r.get("reports"):
        report = "\n\n".join("回执路径：" + path + "\n" + textfile(safe(Path(path), store))
                             for path in r["reports"][-3:])
    context_path = safe(task.parent.parent / "context.md", store)
    context = textfile(context_path)
    latest_review = s["reviews"][-1] if s["reviews"] else None
    def bounded(text):
        return text if len(text) <= 12000 else text[:12000] + "\n[已截断，请读取上述完整文件]"
    argv = [sys.executable, str(Path(__file__).resolve()), "--root",
            str(store.parent), "show", "--task", str(task)]
    if os.name == "nt":
        # PowerShell literal quoting handles spaces, Unicode, # and apostrophes.
        command = "& " + " ".join("'" + part.replace("'", "''") + "'" for part in argv)
    else:
        command = " ".join(shlex.quote(part) for part in argv)
    return "\n".join([
        "请使用 multi-agent-cowork 接手以下任务。本次目的：" + action,
        "任务：" + s["title"], "目标：" + s["goal"],
        "任务记录：" + str(task), "项目根：" + str(store.parent),
        "实际执行工作区：" + s["workspace"],
        "计划版本：%s；状态：%s；状态版本：%s" % (s["revision"], s["status"], s["version"]),
        "完整计划：" + d["plan_path"], "最近回执：" + (r["reports"][-1] if r and r.get("reports") else "尚无"),
        "Feature 背景：" + str(context_path),
        "允许范围：" + json.dumps(s["scope"], ensure_ascii=False),
        "验收：" + json.dumps(s["acceptance"], ensure_ascii=False),
        "依赖任务：" + json.dumps(s["dependencies"], ensure_ascii=False),
        "\nFeature 背景：\n" + bounded(context),
        "\n必要背景与步骤：\n" + bounded(plan),
        "\n最近执行记录：\n" + (bounded(report) if report else "尚无执行回执；核对计划和真实文件。"),
        "\n最近审查：\n" + (latest_review["report"] + "\n" +
                               bounded(textfile(safe(Path(latest_review["report"]), store)))
                              if latest_review else "尚无审查"),
        "\n接手先执行只读查询：\n" + command,
        "重新核对当前版本和真实工作区；提示词不是执行锁或新的权限授权。",
        "若仍有旧执行者写入，先确认暂停/停止；按协议恢复旧 run 后才 claim 新 run。",
        "保留原任务及现存改动，边界内调整步骤并说明；不盲重做、不回滚。",
        "执行/修复后保存改动、实际检查、未运行项、阻塞和剩余步骤的回执。",
        "修好阻塞可暂停交回，也可按用户授权继续。亲自改动后的自查不称独立审查。",
        "本次若仅查询或审查，不因此启动执行。没有本地路径访问能力时说明需要传递的文件。",
        "不要发送消息、启动其他 AI 或扩大原授权。"])


def run(a):
    for field in ("title", "goal", "actor"):
        if hasattr(a, field):
            need(getattr(a, field).strip(), field + " cannot be blank")
    if getattr(a, "acceptance", None):
        need(all(x.strip() for x in a.acceptance), "acceptance cannot be blank")
    root = canonical(a.root)
    store = root / ".ai-cowork"
    if a.command == "init":
        with transaction(store, create=True):
            if (store / "project.json").exists():
                output(project(store, root))
            else:
                p = {"schema": SCHEMA, "id": identity("project"), "root": str(root), "created_at": now()}
                atomic(store / "project.json", p, store)
                output(p)
        return
    project(store, root)
    if a.command == "list":
        items = []
        for p in sorted((store / "features").glob("*/tasks/*/state.json")):
            t = p.parent
            s = state_at(t, store)
            items.append({k: s[k] for k in ("id", "feature", "title", "status", "version", "workspace")})
            items[-1]["task_path"] = str(t)
        output(items)
        return
    if a.command in {"show", "handoff"}:
        t = find_task(store, a.task)
        s = state_at(t, store)
        if a.command == "show":
            output(describe(t, s))
        else:
            print(handoff(t, s, a.action, store))
        return
    with transaction(store):
        if a.command == "feature":
            fid = a.id or identity("feature")
            need(fid.startswith("feature-") and "/" not in fid and ".." not in fid, "invalid feature ID")
            f = store / "features" / fid
            if (f / "feature.json").exists():
                output(load(f / "feature.json", store))
                return
            fdata = {"schema": SCHEMA, "id": fid, "title": a.title, "created_at": now()}
            immutable(f / "context.md", a.context or ("# " + a.title + "\n"), store)
            atomic(f / "feature.json", fdata, store)
            output(fdata)
            return
        if a.command == "task":
            need("/" not in a.feature and ".." not in a.feature, "invalid feature")
            f = store / "features" / a.feature
            load(f / "feature.json", store)
            workspace = canonical(a.workspace or root)
            need(workspace == root or (workspace / ".git").exists() or
                 (workspace / ".ai-cowork" / "project.json").is_file(),
                 "external workspace must be an initialized project or Git worktree")
            scope_check(a.scope)
            plan = textfile(a.plan)
            for dep in a.depends:
                state_at(find_task(store, dep), store)
            t = f / "tasks" / identity("task")
            immutable(t / "plans" / "0001.md", plan, store)
            s = {"schema": SCHEMA, "id": t.name, "feature": a.feature, "title": a.title,
                 "goal": a.goal, "kind": a.kind, "workspace": str(workspace),
                 "scope": a.scope, "acceptance": a.acceptance, "dependencies": a.depends,
                 "revision": 1, "plan_hash": hashlib.sha256(plan.encode()).hexdigest(),
                 "version": 1, "status": "planned", "baseline": snapshot(workspace, a.scope),
                 "active_run": None, "last_run": None, "runs": [], "reviews": [],
                 "created_at": now(), "updated_at": now()}
            atomic(t / "state.json", s, store)
            output(describe(t, s))
            return
        t = find_task(store, a.task)
        s = state_at(t, store)
        expected(s, a)
        if a.command == "claim":
            valid = {"planned", "paused", "blocked", "changes_requested"}
            if a.purpose == "repair":
                valid.add("awaiting_review")
            need(s["status"] in valid, "task not claimable; inspect status or request repair explicitly")
            for dep in s["dependencies"]:
                need(state_at(find_task(store, dep), store)["status"] in {"accepted", "completed"},
                     "dependency not delivered: " + dep)
            current = snapshot(s["workspace"], s["scope"])
            need(current["hash"] == s["baseline"]["hash"], "workspace drift; reconcile before claim")
            r = {"id": identity("run"), "token": uuid.uuid4().hex, "actor": a.actor,
                 "session": a.session, "purpose": a.purpose, "revision": s["revision"],
                 "status": "running", "started_at": now(), "reports": []}
            acquire(s["workspace"], {"task": str(t), "run": r["id"], "token": r["token"],
                                     "actor": a.actor, "created_at": now()})
            # Any failure from here leaves an inspectable lock; never clear an uncertain run.
            s["runs"].append(r)
            s["active_run"] = s["last_run"] = r["id"]
            s["status"] = "running"
            save(t, s, store)
            output({"task_path": str(t), "version": s["version"], "run": r["id"], "token": r["token"]})
        elif a.command in {"checkpoint", "finish"}:
            r = active(s, a, t)
            report = textfile(a.report)
            disposition = a.disposition if a.command == "checkpoint" else a.outcome
            if disposition == "completed":
                need(s["kind"] == "research" or bool(a.waive_review),
                     "change tasks need review or explicit user waiver")
                r["review_waiver"] = a.waive_review
            path = receipt(t, r["id"], report, store, a.command)
            r["reports"].append(path)
            s["baseline"] = snapshot(s["workspace"], s["scope"])
            if disposition != "continue":
                r["status"] = disposition
                r["ended_at"] = now()
                s["active_run"] = None
                s["status"] = disposition
            save(t, s, store)
            if disposition != "continue":
                release(s["workspace"], t, r["id"], a.token)
            output(describe(t, s))
        elif a.command == "recover":
            need(a.reason.strip() and a.stopped_evidence.strip(), "reason and actual stop evidence required")
            owner = lock_record(s["workspace"])
            need(owner.get("task") == str(t) and owner.get("run") == a.expect_run,
                 "recovery must target the exact owner")
            if owner["operation"] == "review":
                need(s["active_run"] is None and s["status"] != "running",
                     "review lock conflicts with live execution")
                path = t / "recoveries" / (identity("review-recovery") + ".md")
                immutable(path, "# Review lock recovery\n\nReason: " + a.reason +
                          "\n\nStop evidence: " + a.stopped_evidence + "\n", store)
                s.setdefault("recoveries", []).append({"lock_run": a.expect_run,
                                                       "report": str(path), "at": now()})
                save(t, s, store)
                release(s["workspace"], t, a.expect_run, owner["token"])
                output(describe(t, s))
                return
            r = next((r for r in s["runs"] if r["id"] == a.expect_run), None)
            if r is None:
                need(s["active_run"] is None and s["status"] != "running",
                     "unknown orphan conflicts with active state")
                r = {"id": a.expect_run, "token": owner.get("token"), "actor": owner.get("actor"),
                     "revision": s["revision"], "status": "interrupted", "reports": [],
                     "orphan": True}
                s["runs"].append(r)
                s["last_run"] = r["id"]
                s["status"] = "paused"
            else:
                need(r.get("token") == owner.get("token"), "recovery token mismatch")
                need(s.get("active_run") in {None, r["id"]} and s.get("last_run") == r["id"],
                     "recovery targets superseded run")
                if r["status"] == "running":
                    r["status"] = "interrupted"
                    s["status"] = "paused"
            path = receipt(t, r["id"], "# Recovery\n\nReason: " + a.reason +
                           "\n\nStop evidence: " + a.stopped_evidence + "\n", store, "recovery")
            r["reports"].append(path)
            r["ended_at"] = now()
            s["active_run"] = None
            # Preserve the submitted evidence for terminal runs. Clearing a residual
            # lock must never bless unreported edits as the old completed result.
            if s["status"] in {"paused", "blocked"}:
                s["baseline"] = snapshot(s["workspace"], s["scope"])
            save(t, s, store)
            release(s["workspace"], t, r["id"], owner["token"])
            output(describe(t, s))
        elif a.command == "revise":
            need(s["status"] not in {"running", "accepted", "completed"}, "cannot revise active/closed task")
            need(not lockpath(s["workspace"]).exists(), "workspace occupied; reconcile before revise")
            plan = textfile(a.plan)
            if a.scope:
                scope_check(a.scope)
                s["scope"] = a.scope
            if a.acceptance:
                s["acceptance"] = a.acceptance
            s["revision"] += 1
            immutable(t / "plans" / ("%04d.md" % s["revision"]), plan, store)
            s["plan_hash"] = hashlib.sha256(plan.encode()).hexdigest()
            s["baseline"] = snapshot(s["workspace"], s["scope"])
            s["status"] = "planned"
            save(t, s, store)
            output(describe(t, s))
        elif a.command == "review":
            need(s["status"] == "awaiting_review" and s["active_run"] is None, "task not awaiting review")
            need(s["revision"] == a.revision and s["last_run"] == a.expect_run,
                 "stale plan/run review")
            r = next(r for r in s["runs"] if r["id"] == a.expect_run)
            need(r["revision"] == s["revision"], "submitted run belongs to old plan")
            if a.review_kind == "independent":
                need(not any(x["actor"] == a.actor for x in s["runs"]),
                     "a participant in this task's execution cannot claim independent review")
            if a.review_kind == "self-check" and a.verdict == "accepted":
                need(a.waiver and a.waiver.strip(), "self-check acceptance requires user waiver")
            report = textfile(a.report)
            rid, token = identity("review"), uuid.uuid4().hex
            acquire(s["workspace"], {"task": str(t), "run": rid, "token": token, "operation": "review",
                                     "actor": a.actor, "created_at": now()})
            try:
                current = snapshot(s["workspace"], s["scope"])
                need(current["hash"] == a.expected_evidence == s["baseline"]["hash"],
                     "review evidence changed; inspect and obtain a fresh execution receipt")
                path = t / "reviews" / (rid + ".md")
                immutable(path, report, store)
                s["reviews"].append({"id": rid, "actor": a.actor, "kind": a.review_kind,
                                     "verdict": a.verdict, "revision": a.revision, "run": a.expect_run,
                                     "evidence": current["hash"], "report": str(path), "at": now(),
                                     "waiver": a.waiver})
                s["status"] = "awaiting_review" if a.verdict == "insufficient_evidence" else a.verdict
                save(t, s, store)
            finally:
                release(s["workspace"], t, rid, token)
            output(describe(t, s))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=os.getcwd(), help="project metadata root; normalized to Git/registered root")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="initialize local project records")
    sub.add_parser("list", help="read task names/status without selecting latest")
    f = sub.add_parser("feature")
    f.add_argument("--title", required=True)
    f.add_argument("--id")
    f.add_argument("--context", default="")
    t = sub.add_parser("task")
    for arg in ("feature", "title", "goal", "plan"):
        t.add_argument("--" + arg, required=True)
    t.add_argument("--scope", action="append", required=True)
    t.add_argument("--acceptance", action="append", required=True)
    t.add_argument("--depends", action="append", default=[])
    t.add_argument("--workspace")
    t.add_argument("--kind", choices=["change", "research"], default="change")
    for name in ("show", "handoff", "claim", "checkpoint", "finish", "recover", "revise", "review"):
        q = sub.add_parser(name)
        q.add_argument("--task", required=True)
        if name in {"show", "handoff"}:
            if name == "handoff":
                q.add_argument("--action", choices=["plan", "execute", "repair", "review", "status"], default="execute")
            continue
        q.add_argument("--expect-version", required=True, type=int)
        if name == "claim":
            q.add_argument("--actor", required=True)
            q.add_argument("--session")
            q.add_argument("--purpose", choices=["execute", "repair"], default="execute")
        elif name in {"checkpoint", "finish"}:
            q.add_argument("--token", required=True)
            q.add_argument("--report", required=True)
            if name == "checkpoint":
                q.add_argument("--disposition", choices=["continue", "paused", "blocked"], default="continue")
            else:
                q.add_argument("--outcome", choices=["awaiting_review", "completed"], default="awaiting_review")
                q.add_argument("--waive-review")
        elif name == "recover":
            q.add_argument("--expect-run", required=True)
            q.add_argument("--reason", required=True)
            q.add_argument("--stopped-evidence", required=True)
        elif name == "revise":
            q.add_argument("--plan", required=True)
            q.add_argument("--scope", action="append")
            q.add_argument("--acceptance", action="append")
        elif name == "review":
            q.add_argument("--actor", required=True)
            q.add_argument("--revision", required=True, type=int)
            q.add_argument("--expect-run", required=True)
            q.add_argument("--expected-evidence", required=True)
            q.add_argument("--verdict", choices=["accepted", "changes_requested", "insufficient_evidence"], required=True)
            q.add_argument("--report", required=True)
            q.add_argument("--review-kind", choices=["independent", "self-check", "human"], default="independent")
            q.add_argument("--waiver")
    return p


if __name__ == "__main__":
    try:
        run(parser().parse_args())
    except (Conflict, OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(json.dumps({"error": str(exc), "action": "inspect records; do not force-clear or blindly retry"},
                         ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
