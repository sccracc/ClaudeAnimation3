import wave, numpy as np, json, re
def load(p):
    w=wave.open(p); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768; return x,w.getframerate()
def pauses(x,sr,min_len=0.14,thr_db=-38):
    hop=int(sr*0.01); n=len(x)//hop
    e=np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)+1e-12) for i in range(n)])
    db=20*np.log10(e+1e-9); ref=np.percentile(db,95); sil=db<ref+thr_db+20 if False else db<(ref-30)
    out=[];i=0
    while i<n:
        if sil[i]:
            j=i
            while j<n and sil[j]: j+=1
            if (j-i)*0.01>=min_len: out.append((i*0.01,j*0.01))
            i=j
        else: i+=1
    return out, n*0.01
def words_timeline(text, x, sr):
    """Assign each word a start time: distribute speech segments (between pauses) over word chunks split at punctuation."""
    ps,dur=pauses(x,sr)
    # speech segments
    segs=[];t=0
    for a,b in ps:
        if a>t+0.05: segs.append((t,a))
        t=b
    if dur>t+0.05: segs.append((t,dur))
    return segs, ps, dur
if __name__=="__main__":
    S=json.load(open("script/script.json"))
    for s in S:
        x,sr=load("audio/vo/%s.wav"%s["id"])
        segs,ps,dur=words_timeline(s["text"],x,sr)
        chunks=[c.strip() for c in re.split(r'(?<=[.,:?])\s+',s["text"]) if c.strip()]
        print(s["id"],round(dur,2),"segs",len(segs),"chunks",len(chunks))
        print("  ",[(round(a,2),round(b,2)) for a,b in segs])

def word_times(sid, text):
    """Estimate each word's start/end time: spread words over speech segments by syllable-ish weight."""
    x,sr=load("audio/vo/%s.wav"%sid)
    segs,ps,dur=words_timeline(text,x,sr)
    words=text.split()
    wts=np.array([max(2,len(re.sub(r'[^A-Za-z0-9]','',w)))+1.5 for w in words],float)
    tot=wts.sum(); speech=sum(b-a for a,b in segs)
    # position in speech-time for each word boundary
    cum=np.concatenate([[0],np.cumsum(wts)])/tot*speech
    def to_real(st):
        acc=0
        for a,b in segs:
            if st<=acc+(b-a)+1e-9: return a+(st-acc)
            acc+=b-a
        return segs[-1][1]
    # snap: words ending in punctuation should end at a pause; do a light correction by nearest pause
    starts=[to_real(c) for c in cum[:-1]]; ends=[to_real(c) for c in cum[1:]]
    pstarts=[a for a,b in ps]; pends=[b for a,b in ps]
    for i,w in enumerate(words):
        if w[-1] in '.,:?;' and i+1<len(words):
            # nearest pause start to ends[i]
            j=int(np.argmin([abs(p-ends[i]) for p in pstarts])) if pstarts else None
            if j is not None and abs(pstarts[j]-ends[i])<0.8:
                ends[i]=pstarts[j]; starts[i+1]=pends[j]
    for i in range(1,len(starts)):
        starts[i]=max(starts[i],starts[i-1]+0.05)
    return [(re.sub(r'[^A-Za-z0-9\-]','',w).lower(),s,e) for w,s,e in zip(words,starts,ends)], dur

if __name__=="__main__" and True:
    out={}
    for s in json.load(open("script/script.json")):
        wt,dur=word_times(s["id"],s["text"])
        out[s["id"]]={"dur":dur,"words":wt}
    json.dump(out,open("script/timing.json","w"),indent=0)
    for k,v in out.items(): print(k, round(v['dur'],2), ' '.join('%s@%.1f'%(w,a) for w,a,b in v['words'][:12]))
