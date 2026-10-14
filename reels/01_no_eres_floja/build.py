import subprocess, json, os
fps=30
lines=[
 (6.501587,"Hoy no pudiste con todo... y ya te estás regañando. Escúchame un momento."),
 (12.538776,"No eres floja. Estás cansada. Llevas meses cargando lo tuyo y lo de los demás, sonriendo para que nadie se preocupe."),
 (17.832925,"Tu cuerpo no te está traicionando. Te está pidiendo una pausa. Descansar no es rendirte. Es echarle agua a la raíz, para que mañana el árbol siga de pie."),
 (10.30966,"Hoy haz una sola cosa por ti: come algo caliente, acuéstate temprano, apaga el teléfono un rato."),
 (7.755465,"Lo que no terminaste hoy, mañana sigue ahí. Pero tú... tú no puedes seguir sin ti."),
 (5.758549,"Mírame bien. No tienes que ganarte el descanso. Ya lo mereces."),
]
LEAD=0.4; GAP=0.4; END=3.6
shots=[(1.15,1.35,.78,.40),(1.35,1.12,.62,.42),(1.0,1.12,.5,.47),(1.12,1.3,.6,.62),(1.2,1.42,.79,.40),(1.42,1.6,.79,.40)]
segs=[]; t=0; starts=[]
for i,(d,_) in enumerate(lines):
    dur=d+GAP+(LEAD if i==0 else 0)+(0.4 if i==len(lines)-1 else 0)
    starts.append(t+(LEAD if i==0 else 0)); segs.append(dur); t+=dur
total=t+END
os.makedirs('clips',exist_ok=True)
for i,((zs,ze,cx,cy),dur) in enumerate(zip(shots,segs)):
    n=round(dur*fps)
    z=f"{zs}+({ze}-{zs})*on/{n}"
    x=f"max(0,min(iw-iw/zoom,{cx}*iw-iw/zoom/2))"; y=f"max(0,min(ih-ih/zoom,{cy}*ih-ih/zoom/2))"
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i','big.png','-vf',f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1080x1920:fps={fps},format=yuv420p",'-frames:v',str(n),'-c:v','libx264','-preset','veryfast','-crf','18',f'clips/s{i}.mp4'],check=True)
n=round(END*fps)
subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i','endbg.png','-vf',f"format=yuv420p",'-frames:v',str(n),'-r',str(fps),'-c:v','libx264','-preset','veryfast','-crf','18','clips/s6.mp4'],check=True)
open('clips/list.txt','w').write(''.join(f"file 's{i}.mp4'\n" for i in range(7)))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','clips/list.txt','-c','copy','base.mp4'],check=True)
# ASS subtitles
def ts(s):
    h=int(s//3600); m=int(s%3600//60); sec=s%60
    return f"{h}:{m:02d}:{sec:05.2f}"
import re
ev=[]
for (d,txt),st in zip(lines,starts):
    words=txt.split()
    chunks=[];cur=[]
    for w in words:
        cur.append(w)
        if len(' '.join(cur))>=16 or re.search(r'[.,:?!…]$',w):
            chunks.append(' '.join(cur)); cur=[]
    if cur: chunks.append(' '.join(cur))
    tot=sum(len(c)+3 for c in chunks); tt=st
    for c in chunks:
        dd=d*(len(c)+3)/tot
        ev.append(f"Dialogue: 0,{ts(tt)},{ts(tt+dd-0.03)},Sub,,0,0,0,,{c.upper()}")
        tt+=dd
ev.append(f"Dialogue: 1,{ts(0)},{ts(3.8)},Hook,,0,0,0,,{{\\fad(150,300)}}NO ERES FLOJA…\\NESTÁS CANSADA")
ee=t
ev.append(f"Dialogue: 1,{ts(ee)},{ts(total)},End,,0,0,0,,{{\\fad(300,0)}}NO TIENES QUE\\NGANARTE\\NEL DESCANSO")
ev.append(f"Dialogue: 1,{ts(ee+0.5)},{ts(total)},Brand,,0,0,0,,{{\\fad(300,0)}}Maestro Mi Güero · Cuentos de Lisi")
ev.append(f"Dialogue: 0,{ts(0)},{ts(ee)},Small,,0,0,0,,Cuentos de Lisi")
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Alegreya Sans ExtraBold,82,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,1,0,1,7,2,2,80,80,430,1
Style: Hook,Alegreya ExtraBold,118,&H006BC9F3,&H00FFFFFF,&H00142030,&H90000000,0,0,0,0,100,100,0,0,1,9,4,8,60,60,250,1
Style: End,Alegreya ExtraBold,124,&H006BC9F3,&H00FFFFFF,&H00142030,&H90000000,0,0,0,0,100,100,0,0,1,8,3,5,60,60,0,1
Style: Brand,Alegreya Sans ExtraBold,52,&H00EAF8FF,&H00FFFFFF,&H00142030,&H90000000,0,0,0,0,100,100,2,0,1,4,0,2,60,60,300,1
Style: Small,Alegreya Sans ExtraBold,40,&H00EAF8FF,&H00FFFFFF,&H00142030,&H90000000,0,0,0,0,100,100,2,0,1,4,0,2,60,60,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""+'\n'.join(ev)+'\n'
open('subs.ass','w').write(ass)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','base.mp4','-vf',"ass=subs.ass:fontsdir=fonts",'-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','video_sin_voz.mp4'],check=True)
json.dump({'starts':starts,'total':total},open('timing.json','w'))
print('total',round(total,2),'starts',[round(s,2) for s in starts])
