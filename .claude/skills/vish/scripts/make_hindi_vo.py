"""Natural Hindi / Hinglish line with AI4Bharat Indic Parler-TTS (Apache-2.0, gated on Hugging Face).

Needs: HF_TOKEN in the environment (an account that accepted the terms at huggingface.co/ai4bharat/indic-parler-tts),
       pip install parler-tts  (PyPI)
Usage: python3 make_hindi_vo.py "<Devanagari text>" out_dir [--takes 3] [--speaker Rohit]
Writes take_1.wav … take_N.wav (different seeds) so a person can pick the best by ear.
Then set "audio": "<path to the chosen take>" on that scene in tools/script.json; make_vo.py uses it instead of Kokoro.
UNTESTED until a token is available: check the first run's output by ear and with Parakeet.
"""
import argparse, os, torch, soundfile as sf
from transformers import AutoTokenizer
from parler_tts import ParlerTTSForConditionalGeneration

ap = argparse.ArgumentParser()
ap.add_argument("text"); ap.add_argument("out_dir")
ap.add_argument("--takes", type=int, default=3); ap.add_argument("--speaker", default="Rohit")
a = ap.parse_args()
assert os.environ.get("HF_TOKEN"), "HF_TOKEN is not set"
os.makedirs(a.out_dir, exist_ok=True)
REPO = "ai4bharat/indic-parler-tts"
model = ParlerTTSForConditionalGeneration.from_pretrained(REPO, token=os.environ["HF_TOKEN"]).eval()
tok = AutoTokenizer.from_pretrained(REPO, token=os.environ["HF_TOKEN"])
dtok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
DESC = (f"{a.speaker} speaks in a confident, energetic and urgent tone like a Hindi TV news anchor announcing breaking news, "
        "with a natural Indian accent, at a slightly fast pace. The recording is very clear and close-sounding, "
        "with very high quality audio and no background noise.")
d = dtok(DESC, return_tensors="pt"); p = tok(a.text, return_tensors="pt")
for i in range(a.takes):
    torch.manual_seed(1000 + i)
    with torch.no_grad():
        g = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                           prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
    path = os.path.join(a.out_dir, f"take_{i + 1}.wav")
    sf.write(path, g.cpu().numpy().squeeze(), model.config.sampling_rate); print(path)
