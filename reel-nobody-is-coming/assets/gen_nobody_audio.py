import numpy as np, wave, sys
SR=44100; DUR=18.0; N=int(SR*DUR)
rng=np.random.default_rng(11)
L=np.zeros(N); R=np.zeros(N)
def add(sig,t,g=1.0,pan=0.0,stop=None):
    i=int(t*SR); j=min(N,i+len(sig))
    if stop is not None: j=min(j,int(stop*SR))
    if j<=i: return
    s=sig[:j-i]*g; L[i:j]+=s*(1-pan); R[i:j]+=s*(1+pan)
def tt(d): return np.arange(int(d*SR))/SR
def onepole(x,a):
    y=np.empty_like(x); acc=0.0
    for i,v in enumerate(x): acc+=a*(v-acc); y[i]=acc
    return y
def sweep_lp(x,a0,a1):
    a=np.linspace(a0,a1,len(x)); y=np.empty_like(x); acc=0.0
    for i,v in enumerate(x): acc+=a[i]*(v-acc); y[i]=acc
    return y
def sub_hit(d=2.2,f0=34):   # cinematic bass hit / boom
    t=tt(d); f=f0+90*np.exp(-t/0.05); ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)*np.exp(-t/0.9)
    click=onepole(rng.standard_normal(len(t)),0.25)*np.exp(-t/0.015)*0.8
    return np.tanh((body+click)*1.6)
def tick():
    t=tt(0.06); return (np.sin(2*np.pi*3200*t)+0.5*np.sin(2*np.pi*5100*t))*np.exp(-t/0.008)+rng.standard_normal(len(t))*np.exp(-t/0.004)*0.5
def heart():
    def thump(f,g):
        t=tt(0.3); fr=f+40*np.exp(-t/0.03); return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t/0.09)*g
    s=np.zeros(int(0.6*SR)); a=thump(55,1.0); b=thump(48,0.7); i=int(0.17*SR)
    s[:len(a)]+=a; s[i:i+len(b)]+=b; return np.tanh(s*1.5)
def kick(g=1.0):
    t=tt(0.4); f=45+150*np.exp(-t/0.035); return np.tanh(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.16)*2.2)*g
def clap():
    n=rng.standard_normal(int(0.25*SR)); t=np.arange(len(n))/SR
    e=np.exp(-t/0.06); 
    for o in (0.0,0.011,0.022): e+= (t>=o)*np.exp(-(t-o).clip(0)/0.006)*0.6
    return (n-onepole(n,0.12))*e*0.6
def hat(): n=rng.standard_normal(int(0.06*SR)); return (n-onepole(n,0.6))*np.exp(-np.arange(len(n))/SR/0.012)*0.5
mid=lambda m:440*2**((m-69)/12)
def saw(f,d,det=(0,0.11,-0.09)):
    t=tt(d); return sum(2*((t*f*(1+c/100))%1)-1 for c in det)/len(det)

# 0: bass hit, 1–2.9: low rumble, 2: second hit
add(sub_hit(),0.0,1.0)
r=onepole(rng.standard_normal(int(1.95*SR)),0.012)*12; tr=tt(1.95)
r=(r+0.5*np.sin(2*np.pi*31*tr))*np.minimum(1,tr/0.4)*np.clip((1.95-tr)/0.3,0,1)
add(r,1.0,0.55)
add(sub_hit(2.6,30),2.0,1.0)
# 3,4,5: sharp ticks; 5.3–7: silence
for t0 in (3.0,4.0,5.0): add(tick(),t0,0.55)
# 7,8: heartbeats
add(heart(),7.0,0.9); add(heart(),8.0,1.0)

# 9–14.5 music: dark minor pad that builds; 11–14.4 riser; 14.5–15 pause
bpm=128; beat=60/bpm
prog=[[45,52,57,60],[41,48,53,57],[48,55,60,64],[43,50,55,62]]  # Am F C G
def pad_section(t0,t1,g0,g1,cut):
    bar=4*beat; t=t0; k=0
    while t<t1:
        d=min(bar,t1-t)+0.4; ch=prog[k%4]
        s=sum(saw(mid(m),d) for m in ch)/4; s=sweep_lp(s,0.03+0.1*(t-t0)/(t1-t0),0.05+0.12*(t-t0)/(t1-t0))
        tt_=tt(d); env=np.minimum(1,tt_/0.3)*np.clip((d-tt_)/0.4,0,1)
        g=g0+(g1-g0)*((t-t0)/(t1-t0)); add(s*env,t,g*0.9,stop=cut); t+=bar; k+=1
pad_section(9.0,14.45,0.12,0.5,14.45)
# soft pulse building from 10
for k in range(int((14.45-10)/beat)):
    t0=10+k*beat; add(kick(0.25+0.35*k/9),t0,1.0,stop=14.45)
# rising noise + pitch riser 11–14.4
d=3.4; n=sweep_lp(rng.standard_normal(int(d*SR)),0.01,0.5); tr=tt(d)
add(n*(tr/d)**2*0.6,11.0,1.0)
f=200*2**(tr/d*2.5); add(np.sin(2*np.pi*np.cumsum(f)/SR)*(tr/d)**1.5*0.25,11.0,1.0)
# 15 drop: full energy until hard cut at 17.5
CUT=17.5
add(sub_hit(1.0,32),15.0,0.9,stop=CUT)
add(onepole(rng.standard_normal(int(1.2*SR)),0.5)*np.exp(-tt(1.2)/0.35)*0.5,15.0,1.0,stop=CUT)  # crash
k=0; t0=15.0
while t0<CUT:
    add(kick(1.0),t0,1.0,stop=CUT)
    if k%2==1: add(clap(),t0,0.9,stop=CUT)
    add(hat(),t0+beat/2,0.8,0.25,stop=CUT); add(hat(),t0+beat/4*3,0.4,-0.25,stop=CUT)
    # bass: off-beat A1
    b=saw(mid(33),beat/2,(0,0.05)); b=onepole(b,0.08)*np.exp(-tt(beat/2)/0.12)
    add(b*1.6,t0+beat/2,1.0,stop=CUT)
    k+=1; t0+=beat
lead_ch=[[57,60,64,69],[53,57,60,65]]
for i,ch in enumerate(lead_ch):
    s=sum(saw(mid(m),1.3) for m in ch)/4; s=sweep_lp(s,0.25,0.18); e=np.minimum(1,tt(1.3)/0.01)
    add(s*e*0.55,15.0+i*1.2,1.0,stop=CUT)
add(sub_hit(1.0,32),16.0,0.7,stop=CUT)  # "today." slam

mix=np.stack([L,R],1); mix/=max(1e-9,np.abs(mix).max()); mix*=0.9
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
