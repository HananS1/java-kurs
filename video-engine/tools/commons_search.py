import json,sys,urllib.parse,subprocess,re
def q(term,n=8):
    p={'action':'query','format':'json','generator':'search','gsrnamespace':'6','gsrlimit':str(n),'gsrsearch':term+' filetype:bitmap',
       'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':'1200'}
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
    r=subprocess.run(['curl','-s','-m','30','-A','WegDerDingeVideo/1.0 (https://claude.ai/code; educational map video)',u],capture_output=True,text=True).stdout
    for k in range(6):
        try: d=json.loads(r);break
        except Exception:
            import time;time.sleep(45);r=subprocess.run(['curl','-s','-m','30','-A','WegDerDingeVideo/1.0 (https://claude.ai/code; educational map video)',u],capture_output=True,text=True).stdout
    else: print('ERR');return
    for pg in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda x:x.get('index',0)):
        ii=pg['imageinfo'][0];m=ii.get('extmetadata',{})
        lic=m.get('LicenseShortName',{}).get('value','?');art=re.sub('<[^>]+>','',m.get('Artist',{}).get('value','?'))[:40]
        print(f"  {pg['title'][5:70]:66} {ii['width']}x{ii['height']} | {lic} | {art}")
import time
for t in sys.argv[1:]:
    print('##',t);q(t);time.sleep(30)
