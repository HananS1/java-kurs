import json,sys,urllib.parse,subprocess,re,os
titles=sys.argv[2:];out=sys.argv[1]
p={'action':'query','format':'json','titles':'|'.join('File:'+t for t in titles),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':'1400'}
u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
import time
for k in range(8):
  r=subprocess.run(['curl','-s','-m','30','-A','WegDerDingeVideo/1.0 (https://claude.ai/code; educational map video)',u],capture_output=True,text=True).stdout
  try: d=json.loads(r);break
  except Exception: print('retry',k,r[:60].replace('\n',' '));time.sleep(30)
meta={}
if os.path.exists(out+'/credits.json'): meta=json.load(open(out+'/credits.json'))
for i,pg in enumerate(d['query']['pages'].values()):
  if 'imageinfo' not in pg: print('missing',pg.get('title'));continue
  ii=pg['imageinfo'][0];m=ii['extmetadata']
  fn=re.sub(r'[^A-Za-z0-9]+','_',pg['title'][5:])[:40]+'.jpg'
  subprocess.run(['curl','-s','-m','60','-A','WegDerDingeVideo/1.0 (https://claude.ai/code; educational map video)','-o',f'{out}/{fn}',ii['thumburl']])
  meta[fn]={'title':pg['title'],'license':m.get('LicenseShortName',{}).get('value'),'artist':re.sub('<[^>]+>','',m.get('Artist',{}).get('value','')).strip(),'page':ii['descriptionurl']}
  print(fn,meta[fn]['license'],meta[fn]['artist'][:40])
json.dump(meta,open(out+'/credits.json','w'),ensure_ascii=False,indent=1)
