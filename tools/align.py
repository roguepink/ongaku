"""Suno の歌詞(曲に埋め込み)と whisper の聞き取りを突き合わせ、歌詞1文字ずつに時刻をつける。"""
import json, re, subprocess, sys, difflib

def lyrics_of(mp3):
    out = subprocess.run(["ffmpeg","-hide_banner","-i",mp3,"-f","ffmetadata","-"],capture_output=True,text=True).stdout
    m = re.search(r"lyrics-\w+=(.*?)(?:\n\w+=|\Z)", out, re.S)
    lines = m.group(1).replace("\\\n","\n").strip().split("\n")
    res, sec = [], None
    for l in lines:
        l = l.strip()
        if not l: continue
        if l.startswith("["):
            sec = l.strip("[]").split(" - ")[0]; continue
        res.append({"sec": sec, "text": l})
    return res

def norm(ch): return ch not in " 　、。!?！？・…ー〜~"

def align(mp3, asr):
    lines = lyrics_of(mp3)
    stream = []  # (char, time)
    for seg in json.load(open(asr)):
        if "視聴" in seg["text"]: continue
        for w in seg.get("words", []):
            cs = [c for c in w["word"] if norm(c)]
            if not cs: continue
            # 歌の前の無音まで言葉の頭を伸ばしてしまうことがあるので、1文字0.7秒までに詰める
            start = max(w["start"], w["end"] - 0.7*len(cs))
            d = (w["end"] - start) / len(cs)
            for i, c in enumerate(cs): stream.append((c, start + d*i))
    lyr = [(li, c) for li, L in enumerate(lines) for c in L["text"] if norm(c)]
    a = "".join(c for _,c in lyr); b = "".join(c for c,_ in stream)
    times = [None]*len(lyr)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): times[blk.a+k] = stream[blk.b+k][1]
    matched = sum(t is not None for t in times)
    # 抜けた文字は前後から按分
    known = [i for i,t in enumerate(times) if t is not None]
    for i in range(len(times)):
        if times[i] is None:
            p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
            if p is None: times[i] = times[n] - 0.2*(n-i)
            elif n is None: times[i] = times[p] + 0.2*(i-p)
            else: times[i] = times[p] + (times[n]-times[p])*(i-p)/(n-p)
    out, k = [], 0
    for li, L in enumerate(lines):
        ts = []
        for c in L["text"]:
            if norm(c): ts.append(round(times[k],2)); k += 1
            else: ts.append(None)
        # 句読点・空白は直前の文字と同じ時刻
        last = next(t for t in ts if t is not None)
        ts = [ (last := t) if t is not None else last for t in ts ]
        out.append({"sec": L["sec"], "text": L["text"], "t": ts})
    print(f"{mp3}: 歌詞 {len(a)} 文字のうち {matched} 文字が聞き取りと一致 ({matched/len(a):.0%})", file=sys.stderr)
    return out

if __name__ == "__main__":
    for name in sys.argv[1:]:
        res = align(f"original/{name}.mp3", f"{name}.asr.json")
        json.dump(res, open(f"dist/{name}.lyrics.json","w"), ensure_ascii=False, separators=(",",":"))
        for L in res: print(name, f"{L['t'][0]:6.1f}-{L['t'][-1]:6.1f}", L["text"])
