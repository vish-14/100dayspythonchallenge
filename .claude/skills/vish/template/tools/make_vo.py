"""Builds the voiceover: one Kokoro clip per scene, joined with short pauses.

Voice "Vish warm" (chosen by ear, Oct 2026): an even blend of hm_omega and hm_psi, en-gb pronunciation,
speed 0.9 (CTA 1.0 via script.json), then 1 semitone lower (formants kept) and a clarity chain
(low cut, less mud, presence lift, de-ess, gentle compression). Pitch shifting keeps timing, so the
scene windows written to vo_scenes.json stay valid.
"""
import json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('/root/.cache/hyperframes/tts/models/kokoro-v1.0.onnx', '/root/.cache/hyperframes/tts/voices/voices-v1.0.bin')
VOICE = 0.5 * k.get_voice_style('hm_omega') + 0.5 * k.get_voice_style('hm_psi')
PITCH_SEMITONES = -1.0
CLARITY = ("highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3200:t=q:w=1.0:g=4,"
           "equalizer=f=8000:t=q:w=1.2:g=1.5,deesser=i=0.3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2")
SC = json.load(open('script.json'))
LEAD = 0.25
GAP = {'hook': 0.3, 'problem': 0.45, 'solution': 0.45, 'a1': 0.35, 'a2': 0.35, 'a3': 0.35, 'a4': 0.4, 'key': 0.5}
SR = 24000; parts = [np.zeros(int(LEAD * SR), np.float32)]; t = LEAD; scenes = []
for s in SC:
    a, sr = k.create(s['say'], voice=VOICE, speed=s.get('speed', 0.9), lang='en-gb'); assert sr == SR
    a = np.asarray(a, dtype=np.float32); thr = 0.01 * np.abs(a).max(); idx = np.where(np.abs(a) > thr)[0]
    a = a[max(0, idx[0] - int(0.02 * sr)):idx[-1] + int(0.08 * sr)]
    scenes.append({'id': s['id'], 'vo_start': round(t, 3), 'vo_end': round(t + len(a) / SR, 3)})
    parts.append(a); t += len(a) / SR
    g = GAP.get(s['id'], 0); parts.append(np.zeros(int(g * SR), np.float32)); t += g
sf.write('voiceover_dry.wav', np.concatenate(parts), SR)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'voiceover_dry.wav', '-af',
                f'rubberband=pitch={2 ** (PITCH_SEMITONES / 12):.5f}:formant=preserved,{CLARITY}', '-ar', str(SR), 'voiceover_fx.wav'], check=True)
vo, _ = sf.read('voiceover_fx.wav', dtype='float32')
vo = vo[:sum(len(p) for p in parts)]
vo = vo / np.abs(vo).max() * 0.89
sf.write('voiceover.wav', vo, SR)
subprocess.run(['rm', '-f', 'voiceover_dry.wav', 'voiceover_fx.wav'])
json.dump(scenes, open('vo_scenes.json', 'w'), indent=1)
print(scenes[-1], 'total', round(len(vo) / SR, 2))
