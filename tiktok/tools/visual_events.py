import sys, numpy as np, json
d=np.frombuffer(sys.stdin.buffer.read(),np.uint8).reshape(-1,256,144,3).astype(np.int16)
R,G,B=d[...,0],d[...,1],d[...,2]
white=(R>215)&(G>215)&(B>215)
crim=(R>170)&(G<90)&(B>60)&(B<150)
orange=(R>200)&(G>110)&(G<200)&(B<110)
fr=30
txt=(white|crim)[:,60:220,:].sum((1,2)).astype(float)
dt=np.diff(txt,prepend=txt[0])
ev=[i for i in range(2,len(dt)-2) if dt[i]>25 and dt[i]==dt[i-2:i+3].max()]
og=orange.sum((1,2)).astype(float)
bo=[i for i in range(3,len(og)-2) if og[i]>200 and og[i]-og[i-3]>150 and og[i]==og[i-2:i+3].max()]
lum=d.mean(axis=(1,2,3)); dl=np.diff(lum,prepend=lum[0])
fl=[i for i in range(2,len(dl)-2) if dl[i]>6 and dl[i]==dl[i-2:i+3].max()]
mot=np.abs(np.diff(d.mean(3),axis=0)).mean((1,2))
print('Text erscheint:',' '.join('%.2f'%(i/fr) for i in ev))
print('Explosion/Feuer:',' '.join('%.2f'%(i/fr) for i in bo))
print('Helligkeits-Blitze:',' '.join('%.2f'%(i/fr) for i in fl))
json.dump({'text':[i/fr for i in ev],'blast':[i/fr for i in bo],'flash':[i/fr for i in fl],'motion':mot.tolist()},open(sys.argv[1],'w'))
