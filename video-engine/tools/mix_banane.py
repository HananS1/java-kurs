import subprocess,sys
S=sys.argv[1];dur=float(sys.argv[2]);out=sys.argv[3]
ev=[('swoosh',2.3),('pop',3.45),('ding',7.6),('whoosh',8.4),('pop',10.55),('pop',12.5),('ding',13.36),('swoosh',16.15),('pop',17.2),('swoosh',18.35),
    ('pop',20.3),('swoosh',21.5),('pop',22.0),('ding',23.5),('pop',24.35),('pop',26.05),('ding',28.36),('ding',32.0),('swoosh',32.4),('pop',32.6),('ding',32.45),('pop',16.35),('pop',22.25),('swoosh',38.6),('ding',38.95)]
ev=[e for e in ev if e[1]<dur]
inp=['-framerate','30','-i',f'{S}/frames3/f_%05d.jpg','-i',f'{S}/audio/vo_final3.wav','-ss','16.4','-i',sys.argv[4]]
fc=['[1]apad,asplit=2[vo][sc]',f'[2]volume=-11dB,afade=t=in:d=0.25,afade=t=out:st={dur-1.8}:d=1.8[mu]','[mu][sc]sidechaincompress=threshold=0.02:ratio=3:attack=15:release=350:makeup=1[md]'];labels=['[vo]','[md]']
for i,(n,t) in enumerate(ev):
    inp+=['-i',f'{S}/audio/{n}.wav'];ms=int(t*1000);fc.append(f'[{i+3}]adelay={ms}|{ms},volume=0.7[e{i}]');labels.append(f'[e{i}]')
fc.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,apad[a]')
cmd=['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(fc),'-map','0:v','-map','[a]','-frames:v',str(int(dur*30)),'-t',str(dur),
     '-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-preset','slow','-c:a','aac','-b:a','192k','-movflags','+faststart',out]
subprocess.run(cmd,check=True);print('ok',out)
