import math,os,json,sys,concurrent.futures as cf,subprocess
from PIL import Image
C=sys.argv[1]; OUT=sys.argv[2]
def t(lat,lon,z):
  n=2**z;return (lon+180)/360*n,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n
def get(z,x,y):
  f=f'{C}/{z}_{x}_{y}.jpg'
  if not os.path.exists(f) or os.path.getsize(f)<500:
    subprocess.run(['curl','-s','-m','30','--retry','3','-o',f,f'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg'])
  return f
P={'thai7':(13.5,100.5,7,8),'bkk10':(13.75,100.5,10,8),'bkk13':(13.75,100.52,13,10),
 'alps7':(47.6,11.0,7,8),'fus10':(47.8,13.3,10,8),'fus13':(47.80,13.27,13,10),
 'vlb10':(47.3,9.7,10,8),'vlb13':(47.28,9.72,13,12),'muc10':(48.14,11.58,10,6),'muc13':(48.14,11.58,13,8)}
meta={}
for name,(lat,lon,z,n) in P.items():
  cx,cy=t(lat,lon,z);x0=int(cx)-n//2;y0=int(cy)-n//2
  jobs=[(z,x0+i,y0+j) for i in range(n) for j in range(n)]
  with cf.ThreadPoolExecutor(16) as ex: files=list(ex.map(lambda a:get(*a),jobs))
  im=Image.new('RGB',(256*n,256*n))
  for (zz,x,y),f in zip(jobs,files):
    try: im.paste(Image.open(f).convert('RGB'),((x-x0)*256,(y-y0)*256))
    except Exception as e: print('bad',f)
  from PIL import ImageEnhance
  im=ImageEnhance.Color(im).enhance(1.25); im=ImageEnhance.Contrast(im).enhance(1.12)
  im.save(f'{OUT}/{name}.jpg',quality=92)
  meta[name]={'z':z,'x0':x0,'y0':y0,'n':n}
  print(name,'ok')
json.dump(meta,open(f'{OUT}/meta.json','w'))
