import numpy as np, wave, sys
SR=44100; DUR=20.0; N=int(SR*DUR)
rng=np.random.default_rng(7)
out=np.zeros((N,2))
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig)); s=sig[:j-i]*gain
    out[i:j,0]+=s*(1-pan)*0.5*2**0.5/1.0*0.7071*2**0.5/2*2
    out[i:j,1]+=s*(1+pan)*0.5*2**0.5/1.0*0.7071*2**0.5/2*2
def env(n,a,d):
    t=np.arange(n)/SR; e=np.exp(-t/d); ai=int(a*SR)
    if ai>0: e[:ai]*=np.linspace(0,1,ai)
    return e
def tone(f,dur,a=0.005,d=0.3,partials=((1,1),)):
    n=int(dur*SR); t=np.arange(n)/SR
    s=sum(g*np.sin(2*np.pi*f*m*t) for m,g in partials)
    return s*env(n,a,d)
def lp(x,alpha):
    y=np.empty_like(x); acc=0.0
    for i,v in enumerate(x): acc+=alpha*(v-acc); y[i]=acc
    return y
def whoosh(dur=0.5,rise=True):
    n=int(dur*SR); x=rng.standard_normal(n)
    a=np.linspace(0.02,0.35,n) if rise else np.linspace(0.35,0.02,n)
    y=np.empty(n); acc=0
    for i in range(n): acc+=a[i]*(x[i]-acc); y[i]=acc
    e=np.sin(np.linspace(0,np.pi,n))**2
    return y*e*1.6
def click(f=2400,d=0.012): return tone(f,0.05,0.0005,d)
def kick():
    n=int(0.35*SR); t=np.arange(n)/SR
    f=50+120*np.exp(-t/0.04); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t/0.12)
def ding(f=1318.5): return tone(f,1.6,0.002,0.45,((1,1),(2.76,0.35),(5.4,0.12)))
def thud():
    k=kick()*1.4; n=len(k); nz=lp(rng.standard_normal(n),0.08)*np.exp(-np.arange(n)/SR/0.05)
    return k+nz*1.5

# ---- music bed: 112 bpm, soft pad + kick + hats
bpm=112; beat=60/bpm
chords=[[57,60,64,67],[53,57,60,64],[48,52,55,60],[55,59,62,67]]  # Am7 F C G
mid=lambda m:440*2**((m-69)/12)
t=np.arange(N)/SR
pad=np.zeros(N); bar=4*beat
for b in range(int(DUR/bar)+1):
    ch=chords[b%4]; i0=int(b*bar*SR); i1=min(N,int((b+1)*bar*SR)+int(0.3*SR))
    if i0>=N: break
    tt=np.arange(i1-i0)/SR; e=np.minimum(1,tt/0.25)*np.exp(-tt/3.0)
    pad[i0:i1]+=sum(np.sin(2*np.pi*mid(m)*tt)+0.3*np.sin(2*np.pi*mid(m)*2.003*tt) for m in ch)*e*0.06
bed=np.zeros(N)
nb=int(DUR/beat)
for k in range(nb):
    tb=k*beat
    if tb<3.55 or tb>19.2: continue           # intro hook stays sparse; drop lands with the coin
    i=int(tb*SR); s=kick()*0.55; j=min(N,i+len(s)); bed[i:j]+=s[:j-i]
    th=tb+beat/2; i=int(th*SR); h=lp(rng.standard_normal(int(0.05*SR)),0.9)*env(int(0.05*SR),0,0.01)*0.12
    j=min(N,i+len(h)); bed[i:j]+=h[:j-i]
# intro: pad only, low
gain=np.where(t<3.6,0.6,1.0)
fade=np.clip((DUR-t)/1.2,0,1); fadein=np.clip(t/0.3,0,1)
music=(pad*gain+bed)*fade*fadein*0.8
out[:,0]+=music; out[:,1]+=music

# ---- sound design synced to the picture
for k,tw in enumerate([0.15,0.27,0.39,0.51,0.63,0.75]): add(click(1800+k*120,0.02),tw,0.25)
add(whoosh(0.45),1.55,0.35)
add(whoosh(0.4,False),3.15,0.35)
add(whoosh(0.5),3.35,0.4)
add(thud(),3.85,0.55); add(thud(),4.12,0.2)
add(ding(1318.5),4.3,0.35); add(ding(1975.5),4.38,0.18,0.3)
add(whoosh(0.5),6.2,0.4)
name="Nimbus Studio Pvt Ltd"
for k in range(len(name)): add(click(3000+ (k%3)*400,0.008),7.1+k*0.9/len(name),0.22,(-0.3 if k%2 else 0.3))
for k,tr in enumerate([8.2,8.48,8.76]): add(tone(660*(1.122**k),0.25,0.002,0.08,((1,1),(2,0.3))),tr,0.25)
for k in range(22): add(click(2200,0.006),9.5+1.1*(1-(1-k/22)**0.5),0.16)
add(ding(1760),10.6,0.22)
add(thud(),11.35,0.9)
add(whoosh(0.4,False),12.95,0.3)
for k,tc in enumerate([13.9,14.05,14.2]): add(tone(523.25*(1.26**k),0.4,0.002,0.12,((1,1),(3,0.2))),tc,0.25)
add(whoosh(0.4,False),16.2,0.3)
add(ding(1318.5),16.85,0.4); add(ding(1975.5),16.95,0.2,-0.3); add(thud(),16.85,0.3)
add(tone(880,0.5,0.002,0.15,((1,1),(2,0.4))),17.85,0.22)

out/=max(1e-9,np.abs(out).max()); out*=0.89
pcm=(out*32767).astype('<i2')
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok")
