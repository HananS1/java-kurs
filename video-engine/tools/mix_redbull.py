import subprocess,sys
S=sys.argv[1];dur=float(sys.argv[2]);out=sys.argv[3];M=sys.argv[4]
ev=[('swoosh',2.2),('pop',3.0),('pop',6.45),('pop',14.4),('pop',21.0),('pop',28.35),('ding',8.08),('pop',11.4),('ding',14.88),('swoosh',16.1),('pop',16.07),('pop',17.3),('pop',19.5),('ding',22.75),('pop',23.65),
    ('swoosh',27.2),('ding',28.0),('pop',30.4),('pop',32.1),('pop',33.88),('whoosh',36.0),('ding',38.7),('pop',38.75),('pop',38.95),('pop',39.15),('pop',39.35),('ding',42.77)]
inp=['-framerate','30','-i',f'{S}/frames_rb/f_%05d.jpg','-i',f'{S}/rb/audio/vo.mp3','-ss','16.7','-i',M]
fc=['[1]apad,asplit=2[vo][sc]',f'[2]volume=-11dB,afade=t=in:d=0.25,afade=t=out:st={dur-1.8}:d=1.8[mu]','[mu][sc]sidechaincompress=threshold=0.02:ratio=3:attack=15:release=350:makeup=1[md]'];labels=['[vo]','[md]']
for i,(n,t) in enumerate(ev):
    inp+=['-i',f'{S}/audio/{n}.wav'];ms=int(t*1000);fc.append(f'[{i+3}]adelay={ms}|{ms},volume=0.7[e{i}]');labels.append(f'[e{i}]')
fc.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,apad[a]')
cmd=['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(fc),'-map','0:v','-map','[a]','-frames:v',str(int(dur*30)),'-t',str(dur),
     '-c:v','libx264','-pix_fmt','yuv420p','-crf','17','-preset','slow','-c:a','aac','-b:a','192k','-movflags','+faststart',out]
subprocess.run(cmd,check=True);print('ok',out)
