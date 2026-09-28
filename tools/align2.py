import json, re, math, numpy as np, sys
sys.path.insert(0,'tools')
from align import load, words_timeline
def wweight(w): return max(2,len(re.sub(r'[^A-Za-z0-9]','',w)))+1.5
def align(sid, text):
    x,sr=load("audio/vo/%s.wav"%sid)
    segs,ps,dur=words_timeline(text,x,sr)
    words=text.split()
    # chunks by punctuation
    chunks=[];cur=[]
    for i,w in enumerate(words):
        cur.append(i)
        if w[-1] in '.,:?;!': chunks.append(cur);cur=[]
    if cur: chunks.append(cur)
    m=len(chunks); n=len(segs)
    cw=[sum(wweight(words[i]) for i in c) for c in chunks]
    sd=[b-a for a,b in segs]
    rate=sum(sd)/sum(cw)
    INF=1e18
    # dp[i][k]: chunks[0:i] consumed exactly segs[0:k]
    dp=[[INF]*(n+1) for _ in range(m+1)]; bk=[[None]*(n+1) for _ in range(m+1)]
    dp[0][0]=0
    for i in range(1,m+1):
        for k in range(1,n+1):
            for i2 in range(max(0,i-3),i):
                for k2 in range(max(0,k-4),k):
                    if dp[i2][k2]>=INF: continue
                    d=sum(sd[k2:k]); e=sum(cw[i2:i])*rate
                    c=dp[i2][k2]+math.log(d/e)**2*(1+ (i-i2))+0.25*(i-i2-1)+0.05*(k-k2-1)
                    if c<dp[i][k]: dp[i][k]=c; bk[i][k]=(i2,k2)
    i,k=m,n; spans=[]
    while i>0:
        i2,k2=bk[i][k]; spans.append((i2,i,k2,k)); i,k=i2,k2
    spans.reverse()
    out=[None]*len(words)
    for i2,i,k2,k in spans:
        idx=[j for c in chunks[i2:i] for j in c]
        ss=segs[k2:k]; tot=sum(b-a for a,b in ss)
        wts=np.array([wweight(words[j]) for j in idx]); cum=np.concatenate([[0],np.cumsum(wts)])/wts.sum()*tot
        def real(st):
            acc=0
            for a,b in ss:
                if st<=acc+(b-a)+1e-9: return a+(st-acc)
                acc+=b-a
            return ss[-1][1]
        for q,j in enumerate(idx):
            out[j]=(re.sub(r'[^A-Za-z0-9\-]','',words[j]).lower(), real(cum[q]+1e-4), real(cum[q+1]))
    return out,dur
if __name__=="__main__":
    res={}
    for s in json.load(open("script/script.json")):
        wt,dur=align(s["id"],s["text"]); res[s["id"]]={"dur":dur,"words":wt}
    json.dump(res,open("script/timing.json","w"),indent=0)
    for k,v in res.items(): print(k,' '.join('%s@%.2f'%(w,a) for w,a,b in v['words'])[:400],'\n')
