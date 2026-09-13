# Offline extractor-review packet

These tools package the completed local audit for AI-first, human-second review. They do not invoke model APIs or regenerate extraction traces.

## Local inputs

Supply an audit directory containing:

- `selection.json`: frozen groups with complete dated source messages; selected question rows, anonymous aliases, and canonical rendered candidate memories with token counts.
- `results/normalize_v5-<group>.json`, `verify-<group>.json` and `coverage-<question>-<alias>.json`: saved annotations from the completed audit.
- `human-review-notes.json`: a JSON object mapping the ten fixed question IDs in the builder to AI first-pass notes.

These are private local artifacts. A fresh clone does not include them and cannot reproduce semantic grades from aggregate results alone. The existing audit directory already contains them. Do not upload it to Git.

Use the project's existing virtualenv and pinned tiktoken dependency:

```sh
python tools/extractor_review/build_human_review.py --audit-dir /absolute/path/to/local/audit
python tools/extractor_review/check_human_review.py --audit-dir /absolute/path/to/local/audit
```

The builder writes `human-review/REVIEW.md`, ten case cards, full source and memory files, a manifest, and mechanical checks. It writes model identities separately to `human-review-model-map.json`. Keep that map closed until review is finished.

Only `human-review/human-decisions.md` is intended for human edits. The builder creates it if absent and never overwrites it. All human decisions initially remain pending; the tools do not turn AI proposals into approved labels or compute a human-approved score.

The checker verifies source-input hashes and local links, checks case cards for known model-identity fields, and rebuilds in a disposable directory twice with a simulated human edit. It does not validate factual correctness. Source and memory text can still reveal stylistic clues.

The fixed ten-case selection is a diagnostic sample, not an unbiased performance estimate. Original annotation errors and exclusions remain unchanged.
