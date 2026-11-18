# clipsai-exp

An experiment running the [Clips AI](https://www.clipsai.com/) quickstart (`clipsai` 0.2.1) with current versions of its dependencies (WhisperX, pyannote.audio 4.x, recent NLTK), using [uv](https://docs.astral.sh/uv/) and a [marimo](https://marimo.io/) notebook.

## Requirements

- Python 3.11 (pinned in `.python-version`)
- uv
- ffmpeg (used by WhisperX and clipsai for media I/O)
- A Hugging Face token for speaker diarization. You must accept the terms for
  [`pyannote/speaker-diarization-3.1`](https://huggingface.co/pyannote/speaker-diarization-3.1)
  on huggingface.co. The notebook pre-fills the token from your local HF login (`hf auth login`).

## Setup

```bash
uv sync
```

## Usage

Open the notebook in the editor:

```bash
uv run marimo edit clipsai_quickstart.py
```

or run it as an app:

```bash
uv run marimo run clipsai_quickstart.py
```

Then:

1. Enter the path to a video that contains speech.
2. Click **1. Transcribe + find clips**. The notebook transcribes the video with WhisperX, then lists the clips that `ClipFinder` found, with start and end times, durations and transcript text.

The first run downloads the WhisperX models and NLTK data, which can take a while.

## Compatibility shims

`clipsai` 0.2.1 doesn't work as-is with current dependencies. `clipsai_compat.py` patches around this and must be imported **before** `clipsai`:

```python
import clipsai_compat  # noqa: F401
from clipsai import ClipFinder, Transcriber, resize
```

It does two things:

- **NLTK:** stores NLTK data in a private, project-local `nltk_data/` directory, because recent NLTK refuses to download into a group-writable `~/nltk_data`.
- **pyannote.audio 4.x:** replaces `PyannoteDiarizer.__init__` to use the renamed `token=` argument, and wraps the pipeline so it returns an `Annotation` instead of the new `DiarizeOutput`.

## Status

Transcription and clip finding work. Resizing clips (`clipsai.resize`, which uses diarization) and exporting to the output directory are not wired up in the notebook yet.
