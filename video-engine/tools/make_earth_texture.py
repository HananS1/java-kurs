import sys
from PIL import Image, ImageFilter, ImageChops, ImageOps
import numpy as np
Image.MAX_IMAGE_PIXELS=None
d=sys.argv[1]; out=sys.argv[2]
W,H=8192,4096
col=Image.open(d+'/bmng.jpg').convert('RGB').resize((W,H),Image.LANCZOS)
rel=Image.open(d+'/shadedrelief.jpg').convert('L').resize((W,H),Image.LANCZOS)
r=np.asarray(rel,dtype=np.float32)/255
blur=np.asarray(rel.filter(ImageFilter.GaussianBlur(6)),dtype=np.float32)/255
hp=r-blur  # high-pass terrain detail
c=np.asarray(col,dtype=np.float32)/255
# land mask: not ocean (ocean is dark blue in bmng)
land=((c[...,0]+c[...,1])>0.25*2*0.5).astype(np.float32)
land=np.asarray(Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)),dtype=np.float32)/255
c=c*(1+hp[...,None]*2.2*land[...,None])
# slight contrast/saturation punch
g=c.mean(-1,keepdims=True); c=g+(c-g)*1.25; c=np.clip((c-0.02)*1.12,0,1)
Image.fromarray((c*255).astype(np.uint8)).save(out+'/earth.jpg',quality=92)
e=Image.open(d+'/etopo1.jpg').convert('L'); print('etopo',e.size)
e.resize((4096,2048),Image.LANCZOS).save(out+'/bump.jpg',quality=90)
