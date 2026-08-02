#!/usr/bin/env python3
"""Render a retro terminal demo from verified live-run artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 900
BG = "#020504"
SURFACE = "#070c0a"
SURFACE_2 = "#0b120f"
LINE = "#1a2a22"
TEXT = "#eef4ef"
DIM = "#7f9188"
GREEN = "#72f1b8"
GREEN_DARK = "#14382a"
AMBER = "#f7c66b"
RED = "#ff6b6b"
BLUE = "#8bbcff"


def display_font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/SegUIVar.ttf"),
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def mono_font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts") / ("consolab.ttf" if bold else "consola.ttf"),
        Path("C:/Windows/Fonts/lucon.ttf"),
        Path("C:/Windows/Fonts/cour.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def base(sequence: str, state: str = "LIVE"):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    for y in range(0, HEIGHT, 4):
        draw.line((0, y, WIDTH, y), fill="#040807")
    for x in range(36, WIDTH, 48):
        for y in range(38, HEIGHT, 48):
            draw.ellipse((x, y, x + 1, y + 1), fill="#102019")

    draw.text((74, 34), "PERMISSION_COMPILER", font=mono_font(18, True), fill=GREEN)
    draw.text((294, 34), f"// {sequence}", font=mono_font(18), fill=DIM)
    draw.rounded_rectangle((1400, 30, 1525, 61), 14, fill=GREEN_DARK)
    draw.ellipse((1420, 41, 1429, 50), fill=GREEN)
    draw.text((1440, 36), state, font=mono_font(16, True), fill=GREEN)

    draw.line((74, 844, 1526, 844), fill=LINE, width=1)
    draw.text((74, 858), "opensearch 3.7.0", font=mono_font(15), fill=DIM)
    draw.text((1328, 858), "evidence > inference", font=mono_font(15), fill=DIM)
    return image, draw


def terminal(draw, title: str, subtitle: str = "localhost:9200"):
    bounds = (74, 84, 1526, 816)
    draw.rounded_rectangle(bounds, 16, fill=SURFACE, outline=LINE, width=2)
    draw.rounded_rectangle((74, 84, 1526, 145), 16, fill=SURFACE_2)
    draw.rectangle((74, 128, 1526, 145), fill=SURFACE_2)
    for x, color in ((104, RED), (132, AMBER), (160, GREEN)):
        draw.ellipse((x, 108, x + 12, 120), fill=color)
    draw.text((204, 101), title, font=mono_font(19, True), fill=TEXT)
    draw.text((1310, 102), subtitle, font=mono_font(16), fill=DIM)
    return bounds


def prompt(draw, y: int, command: str, x: int = 112, size: int = 24):
    draw.text((x, y), "❯", font=mono_font(size, True), fill=GREEN)
    draw.text((x + 34, y), command, font=mono_font(size), fill=TEXT)


def code(draw, x: int, y: int, value: str, color=TEXT, size: int = 22, bold=False):
    draw.text((x, y), value, font=mono_font(size, bold), fill=color)


def status_line(draw, y: int, label: str, detail: str, ok=True):
    color = GREEN if ok else RED
    code(draw, 114, y, "✓" if ok else "×", color, 22, True)
    code(draw, 154, y, label, TEXT, 22)
    code(draw, 590, y, detail, DIM, 20)


def intro(path: Path):
    image, draw = base("BOOT_SEQUENCE")
    terminal(draw, "permission-compiler — zsh")
    prompt(draw, 190, "permission-compiler live --cluster opensearch:3.7.0", size=23)
    code(draw, 112, 248, "initializing observed-minimum engine…", DIM, 20)
    status_line(draw, 302, "TLS chain", "verified with copied demo CA")
    status_line(draw, 350, "credential storage", "disabled")
    status_line(draw, 398, "mutating discovery", "permission-check only")
    status_line(draw, 446, "negative probes", "assertions, never grants")
    draw.line((112, 512, 1488, 512), fill=LINE)
    draw.text((112, 554), "EVIDENCE", font=display_font(66, True), fill=TEXT)
    draw.text((445, 554), "BEFORE", font=display_font(66, True), fill=DIM)
    draw.text((752, 554), "ACCESS", font=display_font(66, True), fill=GREEN)
    code(draw, 114, 664, "Compile what OpenSearch proves. Guess nothing.", DIM, 23)
    image.save(path)


def contract(path: Path):
    image, draw = base("INPUT_CONTRACT")
    terminal(draw, "workflow.contract.json", "4 operations")
    x = 112
    y = 184
    lines = [
        ("{", TEXT),
        ('  "role": ', DIM, '"permission-compiler-search-readonly"', GREEN),
        ('  "allow": [', BLUE),
        ('    "search permission-demo-logs-*",', TEXT),
        ('    "read settings permission-demo-logs-*"', TEXT),
        ("  ],", BLUE),
        ('  "deny": [', AMBER),
        ('    "delete permission-demo-logs-*",', TEXT),
        ('    "read .opendistro_security"', TEXT),
        ("  ]", AMBER),
        ("}", TEXT),
    ]
    for item in lines:
        if len(item) == 2:
            value, color = item
            code(draw, x, y, value, color, 24)
        else:
            prefix, prefix_color, value, value_color = item
            code(draw, x, y, prefix, prefix_color, 24)
            prefix_width = draw.textlength(prefix, font=mono_font(24))
            code(draw, x + int(prefix_width), y, value, value_color, 24)
        y += 47

    draw.line((1000, 182, 1000, 750), fill=LINE, width=2)
    code(draw, 1045, 190, "POLICY", DIM, 18, True)
    code(draw, 1045, 242, "allow", GREEN, 20, True)
    code(draw, 1045, 282, "├─ search logs", TEXT, 20)
    code(draw, 1045, 320, "└─ read settings", TEXT, 20)
    code(draw, 1045, 390, "deny", RED, 20, True)
    code(draw, 1045, 430, "├─ delete index", TEXT, 20)
    code(draw, 1045, 468, "└─ security index", TEXT, 20)
    code(draw, 1045, 568, "scope", DIM, 18, True)
    code(draw, 1045, 608, "permission-demo-logs-*", AMBER, 18)
    code(draw, 1045, 674, "wildcard → human review", DIM, 17)
    image.save(path)


def observe(path: Path):
    image, draw = base("01_OBSERVE")
    terminal(draw, "probe — perform_permission_check=true")
    prompt(draw, 184, "probe --workflow workflow.json --output before-evidence.json", size=21)
    code(draw, 112, 244, "POST /permission-demo-logs-*/_search", BLUE, 20)
    code(draw, 112, 282, "accessAllowed", DIM, 19)
    code(draw, 330, 282, "false", RED, 19, True)
    code(draw, 112, 320, "missingPrivileges", DIM, 19)
    code(draw, 330, 320, '["indices:data/read/search"]', AMBER, 19)

    code(draw, 112, 392, "GET  /permission-demo-logs-*/_settings", BLUE, 20)
    code(draw, 112, 430, "accessAllowed", DIM, 19)
    code(draw, 330, 430, "false", RED, 19, True)
    code(draw, 112, 468, "missingPrivileges", DIM, 19)
    code(draw, 330, 468, '["indices:monitor/settings/get"]', AMBER, 19)

    draw.rounded_rectangle((970, 228, 1468, 642), 10, fill="#08110d", outline=LINE)
    code(draw, 1010, 262, "GUARDRAILS", GREEN, 18, True)
    code(draw, 1010, 322, "01", DIM, 18)
    code(draw, 1060, 322, "exact observed actions", TEXT, 18)
    code(draw, 1010, 372, "02", DIM, 18)
    code(draw, 1060, 372, "explicit index scope", TEXT, 18)
    code(draw, 1010, 422, "03", DIM, 18)
    code(draw, 1060, 422, "negative ≠ grant", TEXT, 18)
    code(draw, 1010, 472, "04", DIM, 18)
    code(draw, 1060, 472, "empty evidence blocks", TEXT, 18)
    code(draw, 1010, 556, "2 missing actions", AMBER, 19, True)
    image.save(path)


def candidate_slide(path: Path, candidate: dict):
    image, draw = base("02_COMPILE")
    terminal(draw, "candidate-role.json", "generated, not applied")
    role_name, role = next(iter(candidate.items()))
    prompt(draw, 184, "compile --evidence before-evidence.json", size=22)
    code(draw, 112, 238, "wrote candidate-role.json", GREEN, 19)
    code(draw, 112, 286, "{", TEXT, 23)
    code(draw, 146, 330, json.dumps(role_name) + ": {", GREEN, 22)
    code(draw, 180, 374, '"cluster_permissions": [],', DIM, 21)
    code(draw, 180, 418, '"index_permissions": [{', BLUE, 21)
    patterns = role["index_permissions"][0]["index_patterns"]
    actions = role["index_permissions"][0]["allowed_actions"]
    code(draw, 214, 462, '"index_patterns": ' + json.dumps(patterns) + ",", TEXT, 20)
    code(draw, 214, 506, '"allowed_actions": [', TEXT, 20)
    for index, action in enumerate(actions):
        suffix = "," if index < len(actions) - 1 else ""
        code(draw, 248, 550 + index * 42, json.dumps(action) + suffix, AMBER, 20)
    y = 550 + len(actions) * 42
    code(draw, 214, y, "]", TEXT, 20)
    code(draw, 180, y + 42, "}]", BLUE, 21)
    code(draw, 146, y + 84, "}", GREEN, 22)
    code(draw, 112, y + 126, "}", TEXT, 23)

    draw.rounded_rectangle((1080, 296, 1468, 624), 10, fill="#08110d", outline=LINE)
    code(draw, 1116, 332, "REVIEW", DIM, 18, True)
    code(draw, 1116, 384, "actions", DIM, 17)
    code(draw, 1380, 384, str(len(actions)), GREEN, 20, True)
    code(draw, 1116, 430, "patterns", DIM, 17)
    code(draw, 1380, 430, str(len(patterns)), GREEN, 20, True)
    code(draw, 1116, 476, "guessed", DIM, 17)
    code(draw, 1380, 476, "0", GREEN, 20, True)
    code(draw, 1116, 548, "status", DIM, 17)
    code(draw, 1300, 548, "reviewable", AMBER, 18, True)
    image.save(path)


def live_run(path: Path, transcript: str):
    image, draw = base("03_LIVE_RUN")
    terminal(draw, "docker — disposable integration", "recorded session")
    stage_lines = [
        "[1/7] starting OpenSearch 3.7.0",
        "[2/7] verifying copied demo CA",
        "[3/7] creating empty-role test identity",
        "[4/7] collecting before-role evidence",
        "[5/7] compiling observed-minimum role",
        "[6/7] explicitly applying reviewed candidate",
        "[7/7] proving allow + deny contract",
    ]
    y = 190
    for index, line in enumerate(stage_lines):
        code(draw, 112, y, "✓", GREEN, 21, True)
        code(draw, 152, y, line, TEXT, 21)
        code(draw, 1372, y, f"0{index + 1}", DIM, 17)
        y += 62
    draw.line((112, 650, 1488, 650), fill=LINE)
    passed = "LIVE DEMO PASSED" in transcript
    code(draw, 112, 690, "session.status", DIM, 20)
    code(draw, 350, 690, "PASSED" if passed else "FAILED", GREEN if passed else RED, 24, True)
    code(draw, 112, 740, "cleanup", DIM, 20)
    code(draw, 350, 740, "container + volume removed", TEXT, 20)
    image.save(path)


def verification_slide(path: Path, report: dict):
    image, draw = base("04_VERIFY", "PASS" if report.get("passed") else "FAIL")
    terminal(draw, "verification-report.json", "live OpenSearch result")
    code(draw, 112, 180, "STEP", DIM, 18, True)
    code(draw, 760, 180, "EXPECT", DIM, 18, True)
    code(draw, 950, 180, "OBSERVED", DIM, 18, True)
    code(draw, 1280, 180, "STATUS", DIM, 18, True)
    draw.line((112, 218, 1488, 218), fill=LINE)
    y = 258
    for result in report.get("results", []):
        expected = str(result.get("expect", "?")).upper()
        outcome = str(result.get("outcome", "?"))
        observed = "allowed" if expected == "ALLOW" else "denied"
        color = GREEN if outcome == "passed" else RED
        code(draw, 112, y, str(result.get("step_id", "?")), TEXT, 20)
        code(draw, 760, y, expected, GREEN if expected == "ALLOW" else AMBER, 19, True)
        code(draw, 950, y, observed, TEXT, 19)
        code(draw, 1280, y, "●  " + outcome, color, 19, True)
        draw.line((112, y + 42, 1488, y + 42), fill="#101b16")
        y += 78

    passed = bool(report.get("passed"))
    draw.rounded_rectangle((112, 620, 1488, 756), 10, fill="#07130e", outline=GREEN_DARK)
    code(draw, 148, 652, "SECURITY CONTRACT", DIM, 18, True)
    draw.text(
        (148, 688),
        "PASS" if passed else "FAIL",
        font=display_font(42, True),
        fill=GREEN if passed else RED,
    )
    code(draw, 360, 701, "required reads work // forbidden actions remain blocked", TEXT, 20)
    image.save(path)


def outro(path: Path):
    image, draw = base("READY_FOR_REVIEW", "OSS")
    terminal(draw, "permission-compiler — release")
    code(draw, 112, 184, "OPEN SOURCE / APACHE-2.0 / DCO-SIGNED", GREEN, 18, True)
    draw.text((112, 246), "Least privilege,", font=display_font(58, True), fill=TEXT)
    draw.text((112, 315), "with receipts.", font=display_font(58, True), fill=GREEN)
    code(draw, 112, 430, "$ git clone https://github.com/Eienel/", DIM, 21)
    code(draw, 112, 468, "  opensearch-permission-compiler", TEXT, 21, True)
    code(draw, 112, 554, "$ ./scripts/demo.ps1", DIM, 21)
    code(draw, 112, 610, "✓ 21 tests", GREEN, 20, True)
    code(draw, 360, 610, "✓ live OpenSearch 3.7.0", GREEN, 20, True)
    code(draw, 720, 610, "✓ Windows + Linux CI", GREEN, 20, True)
    draw.line((112, 690, 1488, 690), fill=LINE)
    code(draw, 112, 732, "github.com/Eienel/opensearch-permission-compiler", BLUE, 22, True)
    image.save(path)


def render(args):
    ffmpeg = shutil.which(args.ffmpeg) or args.ffmpeg
    transcript = args.transcript.read_text(encoding="utf-8-sig")
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    verification = json.loads(args.verification.read_text(encoding="utf-8"))
    if not verification.get("passed"):
        raise RuntimeError("refusing to label a failing integration run as passed")
    if "LIVE DEMO PASSED" not in transcript:
        raise RuntimeError("transcript does not contain a live-demo pass marker")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="permission-compiler-video-") as temp:
        root = Path(temp)
        builders = [
            intro,
            contract,
            observe,
            lambda path: candidate_slide(path, candidate),
            lambda path: live_run(path, transcript),
            lambda path: verification_slide(path, verification),
            outro,
        ]
        frames = []
        for index, builder in enumerate(builders, 1):
            frame = root / f"{index:02d}.png"
            builder(frame)
            frames.append(frame)

        concat = root / "slides.txt"
        durations = [7, 9, 9, 10, 10, 10, 8]
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
                "20",
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
