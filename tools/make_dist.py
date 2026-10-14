"""曲フォルダの original/ から、配る用のファイルを dist/ に作る。
   音はそのまま(作り直さない)。曲名・ジャケット・歌詞だけを入れ直す。
   使い方: python3 tools/make_dist.py songs/<曲>"""
import json, shutil, sys
from pathlib import Path
from mutagen.id3 import ID3, APIC, USLT, TIT2, TPE1, TALB, TDRC

song = Path(sys.argv[1])
meta = json.loads((song / "song.json").read_text())
for v in meta["versions"]:
    lines = json.loads((song / "dist" / f"{v['key']}.lyrics.json").read_text())
    # [Intro - ...] のような Suno への指示は外し、まとまりごとに空行を入れる
    text, prev = [], None
    for L in lines:
        if prev is not None and L["sec"] != prev: text.append("")
        text.append(L["text"]); prev = L["sec"]
    out = song / "dist" / f"{meta['slug']}-{v['key']}.mp3"
    shutil.copy(song / "original" / f"{v['key']}.mp3", out)
    tags = ID3(out)
    for k in ("APIC", "USLT", "TIT2", "TPE1", "TALB", "TDRC"): tags.delall(k)
    tags.add(TIT2(encoding=3, text=f"{meta['title']}({v['label']})"))
    tags.add(TPE1(encoding=3, text=meta["artist"]))
    tags.add(TALB(encoding=3, text=meta["title"]))
    tags.add(TDRC(encoding=3, text=v["created"][:4]))
    tags.add(USLT(encoding=3, lang="jpn", desc="", text="\n".join(text)))
    tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover",
                  data=(song / "dist" / f"cover-{v['key']}.jpg").read_bytes()))
    tags.save(v2_version=3)
    print(out, f"{out.stat().st_size/1e6:.1f}MB")
