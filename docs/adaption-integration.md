# Adaption integration plan

Current execution scope and spending authorization are recorded in [Qwen training and evaluation plan](qwen-training-evaluation-plan.md). That plan supersedes the original-versus-repaired-first sequence below; retain this document as integration background.

Checked the official guides on 2026-09-10. Credential setup is local only; no
dataset upload, synthetic generation or training job has been started.

## Services

- [AutoScientist](https://docs.adaptionlabs.ai/autoscientist-quickstart) will train
  the extractor student from prompt/completion examples. The SDK reads
  `ADAPTION_API_KEY`. Uploads use a dataset registration, signed upload URL and
  completion request with the file size and SHA-256.
- [Adaptive Data](https://docs.adaptionlabs.ai/adaptive-data-quickstart) will
  generate synthetic training data. Its run endpoint supports `estimate=True`
  to validate the request and obtain a quote without launching generation.
  The guide requires SDK 0.9.0 or newer for its download example.

## Experiment controls

Preserve `work/training_copies_v1/` unchanged. Agent reviews and repair proposals
go in separate directories under `work/repair_agents/`. Review findings against
source text before accepting edits. Any further repaired export gets a new
snapshot, replays dependent memory inputs and records unresolved reviews.

First compare original-data and repaired-data training without synthetic data.
Use the same student checkpoint, split, prompt, training budget and evaluation
configuration. Keep whole histories together. Neither current copy is certified
fully clean; the unchanged dev targets are teacher outputs, not factual gold.

The [AutoScientist create reference](https://docs.adaptionlabs.ai/api/resources/autoscientist/methods/create)
allows automatic model selection and derived training settings. Pin the model
and record resolved settings for both arms. Instruction training fits our
prompt/target pairs. Set augmentation counts to zero for the repair comparison.
Autonomous tuning can choose different hyperparameters, so that experiment would
compare tuned pipelines, not isolate data repair alone. Confirm supported fixed
settings before claiming a controlled data-only comparison.

Later, generate synthetic examples from training histories only. Record parent
example/history IDs, generation configuration and output hashes. Check factual
support, format and dev/final overlap before admitting synthetic rows. Compare
synthetic augmentation as a separate experiment; do not augment dev or final.

## Before any paid job

- Choose the student model and approve an Adaption-specific spending cap.
- Confirm accepted message format, context/output limits and split handling.
  The quickstarts do not establish a history-grouped validation split. Do not
  upload our external dev set for automatic row-level splitting.
- Save the upload payload, its hash, dataset/job IDs and exact SDK/model versions.
- Obtain the Adaptive Data estimate before approving its generation run.
- Track AutoScientist iteration costs and downloaded checkpoint provenance.
  Its internal win rate is not our three-benchmark final answer accuracy.
- Guard submissions with a local job ledger. The documented idempotency key
  only deduplicates an in-progress AutoScientist job; a terminal job can be
  submitted again with the same key.
- Reserve independent final histories before reporting held-out performance.

No SDK or provider-specific uploader has been added yet. Existing exports retain
audit metadata and must be adapted to the verified upload contract, not uploaded
blindly.

## Set the key without displaying it

From the project directory, run:

```sh
.venv/bin/python -c 'from getpass import getpass; from dotenv import set_key; k=getpass("Adaption API key (hidden): "); assert k.strip(), "Key cannot be empty"; set_key(".env", "ADAPTION_API_KEY", k); print("Saved to .env")'
```

Paste the key at the hidden prompt, not in chat or as part of the shell command.
`.env` is ignored by Git; `.env.example` contains only a blank placeholder for
this credential. Verification must report key presence only, never its value.
