#!/usr/bin/env python3
"""Render a sanitized, captioned MP4 from live demo artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 900
BACKGROUND = "#071018"
PANEL = "#101e2a"
TEXT = "#e7f0f7"
MUTED = "#8aa2b5"
CYAN = "#55d6be"
GREEN = "#75e08b"
ORANGE = "#ffbf69"
RED = "#ff6b6b"


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def canvas(title: str, kicker: str):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((65, 55, WIDTH - 65, HEIGHT - 55), 28, fill=PANEL)
    draw.text((105, 90), kicker.upper(), font=font(24, True), fill=CYAN)
    draw.text((105, 135), title, font=font(54, True), fill=TEXT)
    draw.rectangle((105, 215, WIDTH - 105, 219), fill="#1d394b")
    return image, draw


def wrapped(draw, text: str, xy, size=30, fill=TEXT, width=68, spacing=14):
    draw.multiline_text(
        xy,
        textwrap.fill(text, width=width),
        font=font(size),
        fill=fill,
        spacing=spacing,
    )


def intro(path: Path):
    image, draw = canvas("Permission Compiler", "OpenSearch security, evidenced")
    wrapped(
        draw,
        "Compile real permission-check evidence into a narrow, reviewable "
        "least-privilege role candidate.",
        (105, 285),
        size=38,
        width=56,
    )
    draw.text((105, 690), "Disposable live integration • OpenSearch 3.7.0", font=font(29), fill=CYAN)
    draw.text((105, 745), "No guessed permissions. No production role auto-apply.", font=font(27), fill=MUTED)
    image.save(path)


def contract(path: Path):
    image, draw = canvas("The security contract", "Four representative operations")
    rows = [
        ("ALLOW", "Search logs on permission-demo-logs-*", GREEN),
        ("ALLOW", "Read settings on permission-demo-logs-*", GREEN),
        ("DENY", "Delete the demo index", RED),
        ("DENY", "Read the Security plugin system index", RED),
    ]
    y = 285
    for label, detail, color in rows:
        draw.rounded_rectangle((105, y, 310, y + 88), 18, fill="#162936")
        draw.text((145, y + 23), label, font=font(27, True), fill=color)
        draw.text((350, y + 23), detail, font=font(29), fill=TEXT)
        y += 112
    image.save(path)


def process(path: Path):
    image, draw = canvas("Observe → compile → verify", "Explicit, reviewable workflow")
    stages = [
        ("1", "Probe safely", "perform_permission_check=true"),
        ("2", "Compile evidence", "observed minimum only"),
        ("3", "Apply in demo", "explicit harness action"),
        ("4", "Verify contract", "allow stays allow; deny stays deny"),
    ]
    y = 270
    for number, heading, detail in stages:
        draw.ellipse((110, y, 180, y + 70), fill="#173b48")
        draw.text((135, y + 16), number, font=font(29, True), fill=CYAN)
        draw.text((215, y), heading, font=font(34, True), fill=TEXT)
        draw.text((215, y + 43), detail, font=font(25), fill=MUTED)
        if number != "4":
            draw.line((145, y + 77, 145, y + 112), fill="#31596c", width=5)
        y += 130
    image.save(path)


def candidate_slide(path: Path, candidate: dict):
    image, draw = canvas("The compiled candidate", "Exact grants backed by evidence")
    role_name, role = next(iter(candidate.items()))
    draw.text((105, 270), role_name, font=font(31, True), fill=CYAN)
    lines = []
    for permission in role.get("index_permissions", []):
        patterns = ", ".join(permission.get("index_patterns", []))
        actions = permission.get("allowed_actions", [])
        lines.append(f"index_patterns: {patterns}")
        lines.extend(f"  + {action}" for action in actions)
    if role.get("cluster_permissions"):
        lines.append("cluster_permissions:")
        lines.extend(f"  + {action}" for action in role["cluster_permissions"])
    if not lines:
        lines = ["No grants were compiled."]
    draw.rounded_rectangle((105, 330, WIDTH - 105, 750), 18, fill="#09141d")
    draw.multiline_text(
        (145, 365),
        "\n".join(lines[:13]),
        font=font(24),
        fill=TEXT,
        spacing=11,
    )
    image.save(path)


def verification_slide(path: Path, report: dict):
    passed = bool(report.get("passed"))
    image, draw = canvas(
        "Verification passed" if passed else "Verification failed",
        "Live OpenSearch result",
    )
    draw.text(
        (105, 270),
        "PASS" if passed else "FAIL",
        font=font(68, True),
        fill=GREEN if passed else RED,
    )
    y = 390
    for result in report.get("results", []):
        expectation = str(result.get("expect", "?")).upper()
        outcome = str(result.get("outcome", "?"))
        color = GREEN if outcome == "passed" else ORANGE
        draw.text((105, y), expectation, font=font(25, True), fill=color)
        draw.text((275, y), str(result.get("step_id", "?")), font=font(28), fill=TEXT)
        draw.text((1120, y), outcome, font=font(25, True), fill=color)
        y += 75
    draw.text(
        (105, 755),
        f"Observed {sum(int(r.get('observations', 0)) for r in report.get('results', []))} permission-check responses",
        font=font(24),
        fill=MUTED,
    )
    image.save(path)


def transcript_slide(path: Path, transcript: str):
    image, draw = canvas("Live run transcript", "Credential-free console output")
    safe_lines = []
    for line in transcript.splitlines():
        lowered = line.lower()
        if (
            not line.strip()
            or "password" in lowered
            or "authorization" in lowered
            or line.startswith("********")
            or "powershell transcript" in lowered
            or lowered.startswith("end time:")
            or "fullyqualifiederrorid" in lowered
            or "categoryinfo" in lowered
            or lowered.startswith("at c:\\")
            or line.strip() == "permission-compiler-opensearch"
            or line.lstrip().startswith("+")
        ):
            continue
        if line.startswith("Artifacts:"):
            line = "Artifacts: ./integration/build"
        safe_lines.append(line)
    safe_lines = safe_lines[-15:]
    draw.rounded_rectangle((105, 265, WIDTH - 105, 765), 18, fill="#050b10")
    draw.multiline_text(
        (135, 295),
        "\n".join(safe_lines),
        font=font(22),
        fill="#c8dbe8",
        spacing=8,
    )
    image.save(path)


def outro(path: Path):
    image, draw = canvas("Evidence before access", "Open source proof of concept")
    wrapped(
        draw,
        "The compiler produces a candidate and a machine-readable review report. "
        "Humans retain the decision to apply it.",
        (105, 295),
        size=36,
        width=58,
    )
    draw.text((105, 600), "github.com/Eienel/opensearch-permission-compiler", font=font(31, True), fill=CYAN)
    draw.text((105, 680), "Apache-2.0 • DCO-signed commits", font=font(26), fill=MUTED)
    image.save(path)


def render(args):
    ffmpeg = shutil.which(args.ffmpeg) or args.ffmpeg
    transcript = args.transcript.read_text(encoding="utf-8-sig")
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    verification = json.loads(args.verification.read_text(encoding="utf-8"))
    if not verification.get("passed"):
        raise RuntimeError("refusing to label a failing integration run as passed")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="permission-compiler-video-") as temp:
        root = Path(temp)
        builders = [
            intro,
            contract,
            process,
            lambda path: candidate_slide(path, candidate),
            lambda path: transcript_slide(path, transcript),
            lambda path: verification_slide(path, verification),
            outro,
        ]
        frames = []
        for index, builder in enumerate(builders, 1):
            path = root / f"{index:02d}.png"
            builder(path)
            frames.append(path)
        concat = root / "slides.txt"
        durations = [6, 8, 8, 10, 10, 9, 7]
        entries = []
        for frame, duration in zip(frames, durations):
            entries.extend([f"file '{frame.as_posix()}'", f"duration {duration}"])
        entries.append(f"file '{frames[-1].as_posix()}'")
        concat.write_text("\n".join(entries) + "\n", encoding="utf-8")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-vf",
                "fps=30,format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "22",
                "-movflags",
                "+faststart",
                str(args.output),
            ],
            check=True,
        )


def parser():
    result = argparse.ArgumentParser()
    result.add_argument("--transcript", type=Path, required=True)
    result.add_argument("--candidate", type=Path, required=True)
    result.add_argument("--verification", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--ffmpeg", default="ffmpeg")
    return result


if __name__ == "__main__":
    render(parser().parse_args())
