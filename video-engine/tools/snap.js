const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('console',m=>{if(m.type()==='error'||m.type()==='warning')console.log('C:',m.text())});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8765/video.html');await p.waitForFunction('window.READY===true',{timeout:180000});
await p.evaluate(w=>window.setWords(w),require(process.env.S+'/build/words_final.json'));
for(const t of process.argv.slice(3).map(Number)){const t0=Date.now();await p.evaluate(t=>window.renderAt(t),t);await p.screenshot({path:`${process.argv[2]}/v_${t}.jpg`,type:'jpeg',quality:85});console.log(t,Date.now()-t0,'ms');}
await b.close();})();
