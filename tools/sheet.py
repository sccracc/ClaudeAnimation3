import sys, glob, subprocess, os
from PIL import Image
ts=sys.argv[1:]
subprocess.run(["rm","-f"]+glob.glob('/home/user/ClaudeAnimation3/build/prev/f_*.png'))
subprocess.run(["python3","-m","anim.render","png"]+ts,cwd="/home/user/ClaudeAnimation3",check=True)
fs=sorted(glob.glob('/home/user/ClaudeAnimation3/build/prev/f_*.png'))
ims=[Image.open(f).resize((640,360)) for f in fs]
c=Image.new('RGB',(1920,360*((len(ims)+2)//3)),(0,0,0))
for i,im in enumerate(ims): c.paste(im,((i%3)*640,(i//3)*360))
c.save('/home/user/ClaudeAnimation3/build/prev/sheet.png')
