"""Original SFX for the breaking-news hook (synthesised, no third-party audio)."""
import numpy as np, soundfile as sf, subprocess, json, sys
OUT = sys.argv[1]; sr = 44100

def onepole_lp(x, fc):
    a = np.exp(-2*np.pi*fc/sr); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x): s = (1-a)*v + a*s; y[i] = s
    return y

# ---------- police siren: rising wail -> fast high-low-high yelps -> falling wail ----------
d = 2.8; t = np.arange(int(sr*d))/sr
f = np.empty_like(t)
lo, hi = 620.0, 1480.0
A = t < 0.85                                     # wail up (fast start, slow top)
f[A] = lo + (hi-lo)*np.sin(0.5*np.pi*t[A]/0.85)**0.8
B = (t >= 0.85) & (t < 2.05)                     # 4 yelps, period 0.3 s: high -> low -> high
ph = ((t[B]-0.85) % 0.3)/0.3
f[B] = lo + 80 + (hi-lo-80)*(0.5+0.5*np.cos(2*np.pi*ph))
C = t >= 2.05                                    # wail down
f[C] = hi - (hi-lo)*np.clip((t[C]-2.05)/0.75, 0, 1)**1.3
def horn(freqs, det=1.0):
    phase = 2*np.pi*np.cumsum(freqs*det)/sr
    x = sum((1.0/n)*np.sin(n*phase) for n in (1, 2, 3, 5, 7)) * 0.55
    return np.tanh(2.2*x)                          # horn-speaker drive
s1 = horn(f); s2 = np.roll(horn(f, 1.03), int(0.045*sr))*0.45   # a second siren behind
env = np.minimum(1, t/0.04) * np.clip((d-t)/0.4, 0, 1)
duck = np.interp(t, [0, 1.25, 1.55, d], [1, 1, 0.32, 0.32])     # drops under the voice
L = (s1 + 0.6*s2)*env*duck; R = (0.8*s1 + s2)*env*duck
sf.write(OUT+'/_siren.wav', np.stack([L, R], 1).astype(np.float32)*0.6, sr)
subprocess.run(['ffmpeg','-v','error','-y','-i',OUT+'/_siren.wav','-af',
  'highpass=f=420,lowpass=f=5200,equalizer=f=1800:t=q:w=1:g=5,aecho=0.85:0.55:70|140:0.32|0.18,alimiter=limit=0.89',
  '-b:a','192k',OUT+'/siren-police.mp3'],check=True)

# ---------- breaking-news sting: DUN - DUN - DUNNN (brass stab + sub boom + noise crack) ----------
d2 = 2.6; t2 = np.arange(int(sr*d2))/sr; x = np.zeros_like(t2)
def saw(fr, tt): return 2*((tt*fr) % 1.0) - 1
chord = [73.42, 110.0, 146.83, 174.61, 220.0]            # D minor, low and wide
for k, (t0, dur, gain) in enumerate([(0.0, 0.28, 0.8), (0.35, 0.28, 0.85), (0.70, 1.6, 1.0)]):
    m = (t2 >= t0); tt = t2[m]-t0
    e = np.exp(-tt/(dur*0.55)) * np.minimum(1, tt/0.006)
    stab = sum(saw(fr*(1+0.004*j), tt) for fr in chord for j in (-1, 1))/len(chord)/2
    boom = np.sin(2*np.pi*np.cumsum(45+40*np.exp(-tt/0.06))/sr)*np.exp(-tt/(0.35 if k < 2 else 0.8))
    crack = np.random.default_rng(k).standard_normal(len(tt))*np.exp(-tt/0.025)
    x[m] += gain*(0.55*stab*e + 0.9*boom + 0.35*crack)
x = onepole_lp(x, 2600)
sf.write(OUT+'/_sting.wav', np.stack([x, x], 1).astype(np.float32)*0.5, sr)
subprocess.run(['ffmpeg','-v','error','-y','-i',OUT+'/_sting.wav','-af',
  'aecho=0.8:0.5:90|180:0.3|0.15,acompressor=threshold=-14dB:ratio=4:attack=2:release=120,alimiter=limit=0.89',
  '-b:a','192k',OUT+'/news-sting.mp3'],check=True)
subprocess.run(['rm',OUT+'/_siren.wav',OUT+'/_sting.wav'])
m = json.load(open(OUT+'/manifest.json'))
m['siren-police'] = {'file':'siren-police.mp3','description':'Original police siren (synthesised): rising wail, fast high-low-high yelps, falling wail; ducks after 1.3 s.','duration':d}
m['news-sting'] = {'file':'news-sting.mp3','description':'Original breaking-news sting (synthesised): three brass/boom hits at 0.0, 0.35, 0.70 s with a long tail.','duration':d2}
json.dump(m, open(OUT+'/manifest.json','w'), indent=1)
print('ok')
