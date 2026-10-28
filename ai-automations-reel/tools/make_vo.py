"""Builds the voiceover: one Kokoro clip per scene (voice hm_omega, Indian English), joined with short pauses."""
import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('/root/.cache/hyperframes/tts/models/kokoro-v1.0.onnx', '/root/.cache/hyperframes/tts/voices/voices-v1.0.bin')
SC = json.load(open('script.json'))
LEAD = 0.25
GAP = {'hook': 0.3, 'problem': 0.35, 'a1': 0.35, 'a2': 0.35, 'a3': 0.35, 'a4': 0.4, 'key': 0.5}
SR = 24000; parts = [np.zeros(int(LEAD * SR), np.float32)]; t = LEAD; scenes = []
for s in SC:
    a, sr = k.create(s['say'], voice='hm_omega', speed=1.0, lang='en-us'); assert sr == SR
    a = np.asarray(a, dtype=np.float32); thr = 0.01 * np.abs(a).max(); idx = np.where(np.abs(a) > thr)[0]
    a = a[max(0, idx[0] - int(0.02 * sr)):idx[-1] + int(0.08 * sr)]
    scenes.append({'id': s['id'], 'vo_start': round(t, 3), 'vo_end': round(t + len(a) / SR, 3)})
    parts.append(a); t += len(a) / SR
    g = GAP.get(s['id'], 0); parts.append(np.zeros(int(g * SR), np.float32)); t += g
vo = np.concatenate(parts); vo = vo / np.abs(vo).max() * 0.89
sf.write('voiceover.wav', vo, SR)
json.dump(scenes, open('vo_scenes.json', 'w'), indent=1)
print(scenes[-1], 'total', round(len(vo) / SR, 2))
