"""Compatibility shims so clipsai 0.2.1 works with current dependencies.

Import this module BEFORE importing clipsai.

1. NLTK: ~/nltk_data is group-writable, so recent NLTK refuses to download
   into it. Point NLTK at a private, project-local directory instead.
2. pyannote.audio 4.x (required by current whisperx):
   - Pipeline.from_pretrained() renamed `use_auth_token` -> `token`
   - pipeline(...) now returns a DiarizeOutput instead of an Annotation
"""

import os
from pathlib import Path

_NLTK_DIR = Path(__file__).resolve().parent / "nltk_data"
_NLTK_DIR.mkdir(mode=0o700, exist_ok=True)
os.environ.setdefault("NLTK_DATA", str(_NLTK_DIR))

import nltk  # noqa: E402

if str(_NLTK_DIR) not in nltk.data.path:
    nltk.data.path.insert(0, str(_NLTK_DIR))

import torch  # noqa: E402
from pyannote.audio import Pipeline  # noqa: E402

import clipsai.diarize.pyannote as _cp  # noqa: E402
from clipsai.utils.pytorch import (  # noqa: E402
    assert_compute_device_available,
    get_compute_device,
)


class _AnnotationPipeline:
    """Wraps a pyannote 4.x pipeline so calling it returns an Annotation."""

    def __init__(self, pipeline):
        self._pipeline = pipeline

    def __call__(self, *args, **kwargs):
        out = self._pipeline(*args, **kwargs)
        return getattr(out, "speaker_diarization", out)

    def __getattr__(self, name):
        return getattr(self._pipeline, name)


def _init(self, auth_token: str, device: str = None) -> None:
    if device is None:
        device = get_compute_device()
    assert_compute_device_available(device)
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", token=auth_token
    )
    if pipeline is None:
        raise RuntimeError(
            "Could not load pyannote/speaker-diarization-3.1. Check your HF token "
            "and that you accepted the model terms on huggingface.co."
        )
    self.pipeline = _AnnotationPipeline(pipeline.to(torch.device(device)))


_cp.PyannoteDiarizer.__init__ = _init
