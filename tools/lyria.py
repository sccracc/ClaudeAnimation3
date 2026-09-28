import json, urllib.request, os, base64, sys
K=os.environ["OPENROUTER_API_KEY"]
def gen(prompt, out):
    p={"model":"google/lyria-3-pro-preview","messages":[{"role":"user","content":prompt}],"modalities":["text","audio"],"audio":{"format":"mp3"},"stream":True}
    r=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(p).encode(),headers={"Authorization":"Bearer "+K,"Content-Type":"application/json"})
    datas=[]; cost=None
    with urllib.request.urlopen(r,timeout=900) as resp:
        for line in resp:
            line=line.decode().strip()
            if not line.startswith("data:") or line[5:].strip()=="[DONE]": continue
            j=json.loads(line[5:])
            if j.get("usage"): cost=j["usage"].get("cost")
            for ch in j.get("choices",[]):
                a=ch.get("delta",{}).get("audio")
                if a and a.get("data"): datas.append(a["data"])
    open(out,"wb").write(b''.join(base64.b64decode(x) for x in datas)); print("cost",cost)
if __name__=="__main__": gen(sys.argv[1], sys.argv[2])
