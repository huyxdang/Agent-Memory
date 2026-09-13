# Local memory review

Open http://127.0.0.1:8085/projects/1/data and click **Label All Tasks**.
This service is local to the machine running it. The existing pilot remains in the original local workspace; this repository contains code only.

## Review a card

1. Read the short source excerpt and the question above it.
2. Check whether the source is clear. Expand the surrounding messages or full actual model input if needed.
3. Read candidate A and B. Grade only the fact asked about, not every statement in the memory.
4. Optionally record the error and a correction. Click **Add** after typing a correction.
5. Click **Submit** to save and continue. Use **Unsure** when you cannot judge confidently.

**Submit before leaving a card.** Unsubmitted choices did not survive a reload in the setup test. Submitted reviews are stored in SQLite and survive restarts. The AI guidance is collapsed by default and is not a human-approved label.

Correct = all requested information is preserved with the right meaning and attribution. Partly preserved = some but not all is retained. Missing = absent. Wrong = the output contradicts or misattributes the requested fact. Unsure = insufficient evidence or confidence.

## What these five cards are

Real saved BEAM dev extraction updates: base Gemma 3 4B Instruct versus its fine-tuned checkpoint. Model identity is hidden and A/B order varies. Both candidates received identical complete message inputs, including prior memory and demonstrations. The displayed excerpt is only a review aid; neither model was given a shortened input for this pilot.

Sources: 100K conversations 10 and 19, first update; 500K conversation 22, first update; 500K conversation 33, updates 2 and 3. Each card covers a different explicitly stated fact. Later updates usually have different accumulated memories, so they are not interchangeable controlled comparisons.

This is a five-card usability/diagnostic pilot, not a representative benchmark score or a three-model ranking. Luna is not included in these paired dev cards. Source histories are benchmark data, not verified real-world user conversations. Dev labels can guide diagnosis/model selection; do not turn these dev examples into training rows while retaining them as held-out dev.

All original model outputs and full inputs remain available. No targets have been repaired, no human grades were prefilled, and no new model calls were made. Source/hash provenance and the private model map live in `private/`; avoid reading the map before grading.

## Start, stop, export

From Terminal:

```sh
cd /path/to/Agent-Memory
.label-studio-venv/bin/python review-tool/manage.py start
.label-studio-venv/bin/python review-tool/manage.py status
.label-studio-venv/bin/python review-tool/manage.py export
# When finished:
.label-studio-venv/bin/python review-tool/manage.py stop
```

Export writes a timestamped JSON file under `review-tool/private/`, including labels and source data. Keep it private. Reopening the project resumes from its stored submissions. Back up the entire `review-tool/data/` directory with the server stopped, plus `review-tool/private/`, to preserve the database, task identity and provenance.

For another browser, username is `reviewer@localhost.test`. Display the generated local-only password in your own terminal:

```sh
.label-studio-venv/bin/python -c 'import json; print(json.load(open("review-tool/private/credentials.json"))["password"])'
```

Do not paste your OpenAI, Modal, Hugging Face or Adaption credentials into Label Studio. This account uses a separate local password.

## Installation and reproducibility

Installed Label Studio 1.23.0 under Python 3.12.13 in the isolated `.label-studio-venv/`. The resolved dependency versions are in `requirements-lock.txt`.

```sh
uv venv --python 3.12 .label-studio-venv
uv pip install --python .label-studio-venv/bin/python -r review-tool/requirements-lock.txt
```

Private review data is deliberately not committed. Before provisioning a new installation, place your existing pilot task package in `review-tool/private/tasks.json`, or rebuild it from the original saved runs. Start the server, wait for `manage.py status` to succeed, then run `manage.py provision`. Use the project URL it prints; project IDs can differ between installations.

The imported pilot is self-contained in `private/tasks.json`. Rebuilding from raw saved runs uses `build_tasks.py` and requires the original audit and run paths referenced in that script. `manage.py provision` imports exactly five tasks and verifies their IDs; repeated calls do not overwrite labels. Changed content is refused rather than silently replacing an existing project.

`check_setup.py` checks the initial clean pilot and verifies a separate synthetic QA annotation. After you begin reviewing it will intentionally fail the “zero real annotations” setup assertion; that is not loss of your work. QA data lives in the clearly named separate project **QA ONLY — synthetic UI test, not human review** and must never enter experiment scores.

Server binds only `127.0.0.1:8085`; remote file serving, analytics, Sentry and version checks are disabled. No external storage or model backend is connected. Do not expose this development server publicly. Only code and documentation belong in Git. Never commit `private/`, `data/`, logs or the virtual environment.
