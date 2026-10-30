"""Original dhol sounds (synthesised): bass head 'dha' + treble stick 'ta'. No third-party audio."""
import numpy as np, soundfile as sf, subprocess, json, sys
OUT = sys.argv[1]; sr = 44100
rng = np.random.default_rng(7)
def dha(d=0.45):
    t = np.arange(int(sr*d))/sr
    f = 70 + 55*np.exp(-t/0.04)
    body = np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t/0.22)
    click = rng.standard_normal(len(t))*np.exp(-t/0.006)*0.35
    return np.tanh(1.6*(body + click))
def ta(d=0.22):
    t = np.arange(int(sr*d))/sr
    f = 380 + 160*np.exp(-t/0.015)
    mem = np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t/0.06)*0.6
    snap = rng.standard_normal(len(t))*np.exp(-t/0.02)
    a = np.exp(-2*np.pi*3000/sr); y = np.zeros_like(snap); s = 0.0
    for i, v in enumerate(snap): s = (1-a)*v + a*s; y[i] = s
    return mem + (snap - y)*0.5                                   # high-passed stick crack
def place(buf, hit, t0, g):
    i = int(t0*sr); n = min(len(hit), len(buf)-i); buf[i:i+n] += g*hit[:n]
def render(pattern, d, name):
    x = np.zeros(int(sr*d))
    for t0, kind, g in pattern: place(x, dha() if kind == 'D' else ta(), t0, g)
    x = x/np.abs(x).max()*0.85
    sf.write(OUT+'/_'+name+'.wav', np.stack([x, x], 1).astype(np.float32), sr)
    subprocess.run(['ffmpeg','-v','error','-y','-i',OUT+'/_'+name+'.wav','-af','aecho=0.8:0.4:45|90:0.25|0.12,volume=9dB,alimiter=limit=0.84','-b:a','192k',OUT+'/'+name+'.mp3'],check=True)
    subprocess.run(['rm',OUT+'/_'+name+'.wav'])
b = 0.15   # 16th-note grid at 100 bpm
intro = [(0,'D',1),(b,'T',.7),(2*b,'T',.6),(3*b,'D',1),(4*b,'T',.7),(5*b,'D',.9),(5.5*b,'T',.6),(6*b,'D',1.1)]
loop = []
for bar in range(4):
    o = bar*8*b
    loop += [(o,'D',.9),(o+2*b,'T',.6),(o+3*b,'T',.5),(o+4*b,'D',.8),(o+6*b,'T',.6),(o+7*b,'T',.5)]
render(intro, 1.6, 'dhol-intro'); render(loop, 4*8*b+0.5, 'dhol-loop')
m = json.load(open(OUT+'/manifest.json'))
m['dhol-intro'] = {'file':'dhol-intro.mp3','description':'Original dhol intro (synthesised): dha ta ta dha ta dha-ta DHA, ends on a big hit at 0.9 s.','duration':1.6}
m['dhol-loop'] = {'file':'dhol-loop.mp3','description':'Original dhol groove (synthesised), 4 bars at 100 bpm, to sit under a voice at low volume.','duration':round(4*8*b+0.5,2)}
json.dump(m, open(OUT+'/manifest.json','w'), indent=1); print('ok')
