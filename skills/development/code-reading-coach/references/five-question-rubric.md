# Five-question rubric

Use this reference when selecting a key method and writing its evidence-backed explanation.

## 1. Position

Identify the business stage first, then the code role:

- request entry or routing;
- parameter parsing and context creation;
- configuration/cache loading;
- rule filtering or eligibility;
- concurrent upstream calls;
- aggregation, combination, parsing, or result assembly;
- fallback, publication, or client-facing serialization.

Name at least one caller and one downstream consumer when the source supports it. If the method is reached through reflection, XML, annotations, or a registry, show that binding explicitly.

## 2. Input and output

Trace actual values rather than generic types. Prefer:

- request fields and their parser;
- context fields before and after mutation;
- cache key or business identifier;
- external request and response object;
- result list, result bucket, JSON field, or status flag;
- who reads the returned value next.

For mutating methods, say “returns void but changes X”, not “has no output”.

## 3. Failure behavior

Check each branch that changes user-visible behavior:

- exception caught, propagated, or converted to an error;
- null, empty list, malformed configuration, or missing required field;
- timeout, rejection, or partial completion;
- feature switch, whitelist, AB, exposure, version, time, or user rule;
- old cache retained, empty cache written, fallback selected, or result omitted;
- whether later stages continue with partial data.

Separate “the code handles this” from “the operational system is known to handle this”.

## 4. Logging and troubleshooting

Search the method and its immediate callers for `log`, UMP, metrics, tracing, alarms, error codes, switches, and request identifiers. Record the actual class/method and line when possible.

Use this diagnostic order:

1. Fix one reproducible request sample and expected result.
2. Confirm the method's input exists and is the expected version.
3. Confirm its output or mutation.
4. Find the first layer where expected data disappears or latency increases.
5. Continue to the next code locator only after the current layer is evidenced.

If observability is absent, report “当前代码未发现足够日志/指标证据” and name the evidence that would close the gap. Never invent a log path or metric.

## 5. Alternative

Only expand this section when the code exposes a meaningful design decision, such as local cache versus remote read, serial versus parallel execution, push notification versus polling, full fallback versus partial result, or one service boundary versus another.

For each serious alternative, compare:

- when it fits;
- what it improves;
- what it costs;
- which failure mode it introduces;
- why the current code may have selected its present design.

If the source does not establish a real design choice, write “暂无必要替代” and do not manufacture an architecture debate.

## Confidence guide

- 9–10/10: exact current source path or explicit user-confirmed operational fact.
- 7–8/10: multiple current code paths agree, but runtime state or historical intent is not proven.
- 4–6/10: reasonable structural inference with incomplete evidence.
- 1–3/10: plausible but unverified; use only as a clearly labeled question or hypothesis.
