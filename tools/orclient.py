import os, json, time, urllib.request
K = os.environ.get("OPENROUTER_API_KEY")
LOG = os.path.join(os.path.dirname(__file__), "..", "audio", "spend_log.jsonl")
BASE = "https://openrouter.ai/api/v1"

def _req(path, payload=None, method="POST"):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"Authorization": "Bearer " + K, "Content-Type": "application/json"})
    return urllib.request.urlopen(r, timeout=300)

def credits():
    with _req("/credits", method="GET") as r:
        return json.load(r)["data"]["total_usage"]

def tts(model, voice, text, out_path, instructions=None, fmt="pcm", extra=None):
    p = {"model": model, "voice": voice, "input": text, "response_format": fmt}
    if instructions: p["instructions"] = instructions
    if extra: p.update(extra)
    for attempt in range(4):
        try:
            with _req("/audio/speech", p) as r:
                gid = r.headers.get("X-Generation-Id"); ct = r.headers.get("Content-Type")
                b = r.read()
            break
        except urllib.error.HTTPError as e:
            print("HTTPError", e.code, e.read()[:400]); 
            if e.code in (400, 401, 402, 404): raise
            time.sleep(2 ** attempt * 2)
    open(out_path, "wb").write(b)
    with open(LOG, "a") as f: f.write(json.dumps({"t": time.time(), "model": model, "gen": gid, "out": out_path, "ct": ct}) + "\n")
    return ct, gid

def chat(model, messages, **kw):
    p = {"model": model, "messages": messages}; p.update(kw)
    with _req("/chat/completions", p) as r:
        d = json.load(r)
    with open(LOG, "a") as f: f.write(json.dumps({"t": time.time(), "model": model, "usage": d.get("usage")}) + "\n")
    return d
