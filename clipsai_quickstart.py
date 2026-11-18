import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    from pathlib import Path

    import marimo as mo

    import clipsai_compat  # noqa: F401  (must come before clipsai)
    import clipsai
    from clipsai import ClipFinder, Transcriber, resize

    return ClipFinder, Path, Transcriber, mo, os


@app.cell
def _(mo):
    mo.md("""
    # Clips AI quickstart

    Example from <https://www.clipsai.com/>, using a uv environment and marimo.

    1. Enter the absolute path to a video below (it must contain speech).
    """)
    return


@app.cell
def _(mo, os):
    video_path = mo.ui.text(
        label="Video path",
        full_width=True,
        value=os.path.expanduser(
            "~/tmp/I Bought TikTok’s Worst Rated Products [4Db8pHI0l1E].mp4"
        ),
    )
    from huggingface_hub import get_token

    hf_token = mo.ui.text(
        label="HF token", kind="password", value=get_token() or ""
    )
    out_dir = mo.ui.text(label="Output dir", value="output")
    mo.vstack([video_path, hf_token, out_dir])
    return (video_path,)


@app.cell
def _(mo):
    transcribe_btn = mo.ui.run_button(label="1. Transcribe + find clips")
    transcribe_btn
    return (transcribe_btn,)


@app.cell
def _(ClipFinder, Path, Transcriber, mo, transcribe_btn, video_path):
    mo.stop(not transcribe_btn.value, mo.md("_Click the button to transcribe._"))
    _p = Path(video_path.value).expanduser().resolve()
    mo.stop(not _p.is_file(), mo.md(f"**File not found:** `{_p}`"))
    video_file = str(_p)

    with mo.status.spinner("Transcribing (WhisperX)..."):
        transcriber = Transcriber()
        transcription = transcriber.transcribe(audio_file_path=video_file)

    with mo.status.spinner("Finding clips..."):
        clips = ClipFinder().find_clips(transcription=transcription)
    return clips, transcription


@app.cell
def _(clips, mo, transcription):
    _rows = [
        {
            "#": i,
            "start": round(c.start_time, 2),
            "end": round(c.end_time, 2),
            "duration": round(c.end_time - c.start_time, 2),
            "text": transcription.text[c.start_char : c.end_char],
        }
        for i, c in enumerate(clips)
    ]
    mo.vstack([mo.md(f"Found **{len(clips)}** clips"), mo.ui.table(_rows)])
    return


if __name__ == "__main__":
    app.run()
