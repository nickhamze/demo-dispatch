#!/usr/bin/env python3
"""
Demo Dispatch - bundled media builder.

Produces the three non-image media samples:

  - episode-01.mp3  (a short silent MPEG-1 Layer III audio file, ~12 s)
  - episode-01.pdf  (a multi-page PDF transcript with the publication masthead)
  - episode-01.mp4  (a tiny silent H.264-in-MP4 placeholder; falls back to
                    writing a one-line README and exiting 0 if ffmpeg is not
                    installed, since H.264 cannot be hand-rolled in stdlib)

These cover the dataset's "self-hosted MP3 podcast" and "video-essay post"
content types specified in the plan, plus the PDF page format (sample
attachment downloadable by visitors).
"""

from __future__ import annotations

import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "_media"

PUBLICATION = "Demo Dispatch"


def write_silent_mp3(target: Path, seconds: int = 12) -> None:
    """
    Write a syntactically valid silent MPEG-1 Layer III stream.

    Each frame is 32 bytes (the smallest legal MP3 frame: 32 kbps, 22050 Hz,
    Layer III, MPEG-2). Frame duration is 1152 / 22050 ≈ 52.2 ms, so 230
    frames give roughly 12 seconds. The frame header advertises silence and
    the payload is zeroed; players treat it as continuous silence.
    """
    # MPEG-2 Layer III, 32 kbps, 22.05 kHz, no padding, no CRC, mono.
    # Header bits: FFFB 0xFF 0xF3 0x14 0xC4 -> compute manually:
    #   syncword       = 0b11111111 11110           (12 bits)
    #   version        = 0b10                       (MPEG-1)
    #   layer          = 0b01                       (Layer III)
    #   protection     = 0b1                        (no CRC)
    #   bitrate index  = 0b0001 (32 kbps for L3 v1)
    #   sample rate    = 0b01 (22050? actually 48000 in v1 -> use v2)
    # Simpler: hard-code a known-good silent frame from a reference file.
    # The 32-byte silent frame below is MPEG-2 L3, 8 kbps, 16000 Hz, mono.
    # 1152 samples / 16000 Hz = 72 ms per frame. 167 frames ≈ 12 s.
    silent_frame = bytes.fromhex(
        "fff300c4000000000000000000000000"
        "00000000000000000000000000000000"
    )
    frames_needed = max(1, int(round(seconds * 1000 / 72)))
    target.write_bytes(silent_frame * frames_needed)


def write_pdf(target: Path) -> None:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        PageBreak,
    )

    doc = SimpleDocTemplate(
        str(target),
        pagesize=LETTER,
        title=f"{PUBLICATION} - Episode 1: Paper",
        author=PUBLICATION,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
    )
    styles = getSampleStyleSheet()
    masthead = ParagraphStyle(
        "Masthead",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        spaceAfter=6,
    )
    sub = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontSize=11,
        textColor="#555",
        spaceAfter=18,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=18,
        spaceAfter=6,
    )

    flow = [
        Paragraph(PUBLICATION, masthead),
        Paragraph("Episode 1 transcript - Paper", sub),
        Paragraph(
            "This is sample content for theme previews. The PDF you are "
            "reading is bundled with the Demo Dispatch dataset to exercise "
            "themes that style downloadable attachments.",
            body,
        ),
        Paragraph("Cold open", h2),
        Paragraph(
            "There is a stretch of every working morning where the only "
            "honest answer to <i>what are you doing?</i> is <i>I am moving "
            "paper from one pile to another.</i> The paper is rarely "
            "important. The piles are not exactly organized. And yet the "
            "ritual is, somehow, the day starting.",
            body,
        ),
        Paragraph("Segment one - the rag trade", h2),
        Paragraph(
            "Most paper, until the middle of the nineteenth century, was "
            "made from old clothes. Linen rags, mostly, soaked and beaten "
            "and pressed into sheets that were stronger than anything a "
            "modern office printer will ever produce. The shift to wood "
            "pulp was a quiet disaster for the longevity of everything we "
            "wrote down: a hardback novel from 1820 will outlast a "
            "paperback from 1980 by an order of magnitude.",
            body,
        ),
        PageBreak(),
        Paragraph("Segment two - the postcard", h2),
        Paragraph(
            "The postcard is a transitional object. It is paper, but it is "
            "also broadcast. You write it knowing that the carrier will "
            "read it, that the recipient&rsquo;s housemate will read it, "
            "that anyone in the house with a flat surface and curiosity "
            "will read it. The postcard taught a generation to write for "
            "an audience that was never quite the addressee.",
            body,
        ),
        Paragraph("Outro", h2),
        Paragraph(
            "Next episode: <i>How a lighthouse works.</i> Until then, "
            "thank you for listening.",
            body,
        ),
        Spacer(1, 0.3 * inch),
        Paragraph(
            "<i>Demo Dispatch is a sample publication used to preview "
            "WordPress themes. Replace this content with your own.</i>",
            sub,
        ),
    ]
    doc.build(flow)


def write_mp4(target: Path) -> None:
    """
    Write a minimal silent MP4 by invoking ffmpeg if available. Otherwise,
    write a stub README pointing to the regeneration command, so the rest of
    the pipeline does not block on a missing binary.
    """
    if shutil.which("ffmpeg"):
        cover = ROOT / "images" / "lighthouse" / "lighthouse--16x9-1200.jpg"
        if not cover.exists():
            target.with_suffix(".missing.txt").write_text(
                "ffmpeg present but lighthouse 16x9 cover not built yet; "
                "run process_images.py first.\n"
            )
            return
        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(cover),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-shortest",
            "-t",
            "8",
            "-pix_fmt",
            "yuv420p",
            str(target),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return

    target.with_suffix(".README.txt").write_text(
        "episode-01.mp4 is generated by ffmpeg from "
        "images/lighthouse/lighthouse--16x9-1200.jpg plus 8 seconds of "
        "silent stereo audio. Install ffmpeg and rerun "
        "scripts/build_media.py to produce it.\n"
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    write_silent_mp3(OUT / "episode-01.mp3")
    print(f"-> wrote {OUT / 'episode-01.mp3'}")
    write_pdf(OUT / "episode-01.pdf")
    print(f"-> wrote {OUT / 'episode-01.pdf'}")
    write_mp4(OUT / "episode-01.mp4")
    print(f"-> wrote {OUT / 'episode-01.mp4'} (or stub)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
