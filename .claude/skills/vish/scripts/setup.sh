#!/usr/bin/env bash
# One-time setup for a fresh container (Claude Code cloud or a local machine).
# Installs the reel + PDF toolchain and pre-downloads the local models. Safe to re-run.
# Usage: bash scripts/setup.sh
set -u
ok()   { printf '  ✓ %s\n' "$1"; }
bad()  { printf '  ✗ %s\n' "$1"; FAIL=1; }
FAIL=0
HF="npx -y hyperframes@0.8.209"

echo "1/5 Node, ffmpeg, Playwright"
command -v node >/dev/null && ok "node $(node -v)" || bad "node missing"
command -v ffmpeg >/dev/null || (apt-get install -y ffmpeg >/dev/null 2>&1 || true)
command -v ffmpeg >/dev/null && ok "ffmpeg" || bad "ffmpeg missing (needed for audio QA and frame checks)"
node -e "require('playwright')" 2>/dev/null && ok "playwright" || bad "playwright missing (Claude Code cloud has it preinstalled; locally: npm i -g playwright && npx playwright install chromium)"

echo "2/5 Python packages"
pip install -q kokoro-onnx soundfile numpy pypdf pypdfium2 pillow >/dev/null 2>&1
python3 -c "import torch, transformers" 2>/dev/null || pip install -q torch --index-url https://download.pytorch.org/whl/cpu >/dev/null 2>&1
python3 -c "import transformers" 2>/dev/null || pip install -q transformers >/dev/null 2>&1
python3 -c "import kokoro_onnx, soundfile, pypdf, pypdfium2, PIL, torch, transformers" 2>/dev/null && ok "python packages" || bad "python packages"

echo "3/5 HyperFrames CLI"
$HF --version >/dev/null 2>&1 && ok "hyperframes 0.8.209" || bad "hyperframes"

echo "4/5 Voice model (Kokoro, ~340 MB once)"
if [ ! -f ~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx ]; then
  (cd /tmp && $HF tts "Setup check." -o /tmp/vish-tts-check.wav >/dev/null 2>&1)
fi
[ -f ~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx ] && [ -f ~/.cache/hyperframes/tts/voices/voices-v1.0.bin ] && ok "kokoro + voices" || bad "kokoro model"

echo "5/5 Word timestamps (Parakeet) and music model (MusicGen, downloads on first use)"
$HF models install parakeet --json < /dev/null >/dev/null 2>&1 && ok "parakeet" || bad "parakeet"
python3 - <<'EOF' >/dev/null 2>&1 && ok "musicgen-small" || bad "musicgen-small (needs huggingface.co access)"
from transformers import AutoProcessor, MusicgenForConditionalGeneration
AutoProcessor.from_pretrained("facebook/musicgen-small"); MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
EOF

[ "$FAIL" = 0 ] && echo "Ready." || echo "Some steps failed: see ✗ above. Network policy must allow npm, PyPI, huggingface.co and github.com."
exit $FAIL
