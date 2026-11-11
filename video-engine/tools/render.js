const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [out,dur,fps]=[process.argv[2],+process.argv[3],+process.argv[4]];fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8765/video.html');await p.waitForFunction('window.READY===true',{timeout:120000});
await p.evaluate(w=>window.setWords(w),require(process.argv[5]));
const n=Math.round(dur*fps);const i0=+(process.argv[6]||0),i1=Math.min(n,+(process.argv[7]||n));for(let i=i0;i<i1;i++){await p.evaluate(t=>window.renderAt(t),i/fps);await p.screenshot({path:`${out}/f_${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close();console.log('done',n);})();
