# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An experiment running the [Clips AI](https://www.clipsai.com/) quickstart (`clipsai` 0.2.1) against current versions of its dependencies, using a uv-managed Python 3.11 environment and a marimo notebook UI.

## Commands

- Install / sync the environment: `uv sync`
- Edit the notebook interactively: `uv run marimo edit clipsai_quickstart.py`
- Run it as a read-only app: `uv run marimo run clipsai_quickstart.py`
- Run as a plain script: `uv run python clipsai_quickstart.py`

There are no tests, linter config, or build step.

## Architecture

- `clipsai_quickstart.py` is a **marimo notebook** stored as Python. Each `@app.cell` function is a reactive cell: its parameters are the variables it reads and its `return` tuple is what it exports to other cells. Keep that contract intact when editing: a name must be returned by exactly one cell before another cell can use it, and names starting with `_` are cell-local. Heavy steps are gated with `mo.ui.run_button` + `mo.stop(...)` so they don't re-run on every UI change.
- `clipsai_compat.py` monkey-patches clipsai so it works with today's dependencies. It **must be imported before `clipsai`**. It does two things:
  1. Points NLTK at a project-local `nltk_data/` (mode 0700), because newer NLTK refuses to download into a group-writable `~/nltk_data`.
  2. Replaces `clipsai.diarize.pyannote.PyannoteDiarizer.__init__` to handle pyannote.audio 4.x, which current whisperx pulls in: `use_auth_token` became `token`, and the pipeline now returns a `DiarizeOutput`, so a wrapper unwraps `.speaker_diarization` back into an `Annotation`.
- Dependency pins in `pyproject.toml` matter: `whisperx` is installed from git (m-bain/whisperx), and `torchaudio` is pinned to `2.8.0`. If you upgrade these, check the compat shims again.
- Diarization (used by `clipsai.resize`) loads the gated `pyannote/speaker-diarization-3.1` model and needs a Hugging Face token whose account has accepted that model's terms. The notebook pre-fills the token from `huggingface_hub.get_token()`.

## Current state

The notebook currently covers transcription (WhisperX) and `ClipFinder` only. The `hf_token` and `out_dir` inputs are defined but not yet wired up (nothing resizes or exports clips yet), and `resize` is imported but not used. `output/`, `nltk_data/`, and `__marimo__/` are generated and gitignored.
