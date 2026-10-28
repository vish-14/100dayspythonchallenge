# Original background music generated locally with MusicGen (facebook/musicgen-small).
import sys, numpy as np, soundfile as sf, torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
torch.manual_seed(int(sys.argv[3]) if len(sys.argv) > 3 else 7)
prompt = sys.argv[2]
proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
inputs = proc(text=[prompt], padding=True, return_tensors="pt")
audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=1500)
sr = model.config.audio_encoder.sampling_rate
x = audio[0, 0].cpu().numpy()
sf.write(sys.argv[1], x, sr)
print("ok", round(len(x) / sr, 2), sr)
