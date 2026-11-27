"""inkling-mini 技能的最小契約測試（不需要模型或 GPU）。"""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
SERVE = ROOT / "scripts" / "serve.sh"


def test_skill_records_verified_executor_and_boundary():
    text = SKILL.read_text(encoding="utf-8")
    required = [
        "b12803",
        "inkling2_loop",
        "inkling2v",
        "0.40.14",
        "b11963",
        "b12257",
        "OpenAI",
        "reasoning_content",
        "92",  # OpenCode 送出的 92k tokens
        "opencode run",
    ]
    for token in required:
        assert token in text, f"SKILL.md 缺少關鍵事實：{token}"


def test_serve_script_is_valid_bash():
    subprocess.run(["bash", "-n", str(SERVE)], check=True)


def test_serve_script_uses_verified_flags():
    text = SERVE.read_text(encoding="utf-8")
    for flag in [
        "--mmproj",
        "--cache-type-k q8_0",
        "--no-repack",
        "--no-warmup",
        "-np 1",
        "-ngl",
        "/health",
    ]:
        assert flag in text, f"serve.sh 缺少已驗證參數：{flag}"
