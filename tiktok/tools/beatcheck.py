import sys, numpy as np
d=np.frombuffer(sys.stdin.buffer.read(),np.uint8).reshape(-1,256,144).astype(float)
lum=d.mean((1,2)); fps=30; BEAT=60/115.75; OFF=0.09
dl=np.diff(lum,prepend=lum[0])
hits=0; tot=0; strengths=[]
for b in range(0,int((56.5-OFF)/BEAT)):
    f=int(round((OFF+b*BEAT)*fps)); w=dl[max(0,f-1):f+2]
    base=np.median(np.abs(dl[max(0,f-8):f-2])) if f>8 else 0.1
    tot+=1; s=w.max()
    strengths.append(s)
    if s>max(0.8,3*base): hits+=1
print(f"Schläge mit sichtbarem Bild-Impuls: {hits}/{tot}  (mittlere Stärke {np.mean(strengths):.1f})")
