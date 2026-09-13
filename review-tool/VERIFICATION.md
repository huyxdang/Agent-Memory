# Setup verification — 2026-09-13

Passed:

- Five unique real tasks, ten original outputs; imported data equals the local task package exactly.
- Complete messages match between base and fine-tuned extractors for every pair. Source excerpts were checked against actual extraction inputs.
- All five real tasks have zero annotations, predictions and review drafts at handoff.
- Label configuration accepted by Label Studio 1.23.0 and rendered in the actual browser. Source, side-by-side A/B updates, choices, raw outputs and expandable full input are present.
- First full-input panel contains 64,277 characters, including demonstrations and the actual source session. The display uses a scroll panel, not source truncation.
- On a separate synthetic QA card, submission without candidate B's grade was rejected with a required-field warning.
- Complete dummy choices and a correction were submitted in the UI. The UI confirmed successful saving.
- JSON export contained the submitted choices. Those choices and the correction remained visible after restarting the server and reloading the browser.
- Re-running provision left the pilot at exactly five tasks; it did not duplicate the import or overwrite annotations.
- Listener verified as TCP 127.0.0.1:8085, not 0.0.0.0. Analytics, Sentry, version checks and local-file serving disabled in launcher configuration.

Limitation found:

- Unsubmitted choices did not survive browser reload. Instructions explicitly require Submit before leaving a card. Do not promise automatic draft recovery.

Not established:

- Human judgment quality, review time, rubric agreement, representative model rankings or any improvement from fine-tuning. These need real human reviews and separate evaluation.
- This pilot compares Gemma base versus fine-tuned only; it does not supply a matched Luna comparison.

The QA annotation is software-test data, not a human-reviewed experiment label. No model inference or external trace upload occurred; model API spend was $0. No commit/push was performed.
