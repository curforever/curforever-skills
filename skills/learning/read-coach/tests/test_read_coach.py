from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "read_coach.py"


def run_script(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


class ReadCoachScriptTests(unittest.TestCase):
    def test_inspect_returns_outline_without_changing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "guide.md"
            original = "# 测试指南\n\n## 第一步\n\n说明文字。\n\n```python\nprint('ok')\n```\n"
            source.write_text(original, encoding="utf-8")

            result = run_script("inspect", "--source", str(source), cwd=folder)

            self.assertEqual(result.returncode, 0, result.stderr)
            inspected = json.loads(result.stdout)
            self.assertEqual(inspected["title"], "测试指南")
            self.assertEqual(len(inspected["headings"]), 2)
            self.assertEqual(inspected["code_blocks"], 1)
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_init_and_append_keep_all_sections_in_one_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "article.md"
            source.write_text("# 一篇文章\n\n正文。\n", encoding="utf-8")
            original = source.read_text(encoding="utf-8")

            initialized = run_script("init", "--source", str(source), cwd=folder)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            report = Path(initialized.stdout.strip())
            content_file = folder / "quick.md"
            content_file.write_text("建议重点学习。", encoding="utf-8")

            appended = run_script(
                "append", "--report", str(report), "--section", "quick", "--content-file", str(content_file), cwd=folder
            )
            self.assertEqual(appended.returncode, 0, appended.stderr)
            report_text = report.read_text(encoding="utf-8")
            for heading in (
                "## 1. 30 秒结论",
                "## 2. 质量评分与依据",
                "## 3. 核心知识地图",
                "## 4. 互动学习记录",
                "## 5. 应用练习与答案要点",
                "## 6. 最终掌握总结与下一步",
            ):
                self.assertIn(heading, report_text)
            self.assertIn("建议重点学习。", report_text)
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_existing_report_requires_explicit_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "article.md"
            source.write_text("# 文章\n\n正文。\n", encoding="utf-8")
            first = run_script("init", "--source", str(source), cwd=folder)
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_script("init", "--source", str(source), cwd=folder)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("报告已存在", second.stderr)


if __name__ == "__main__":
    unittest.main()
