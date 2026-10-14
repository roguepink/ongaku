"""試しのページを作る。
   python3 tools/build_preview.py songs/<曲>            → <曲>/preview.html(同じフォルダのファイルを読む)
   python3 tools/build_preview.py songs/<曲> --single   → 曲も画像も1ファイルに埋め込んだ版(スマホに送る用)"""
import base64, json, sys
from pathlib import Path

song = Path(sys.argv[1]); single = "--single" in sys.argv
meta = json.loads((song / "song.json").read_text())
dist = song / "dist"
def ref(p, mime):
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}" if single else f"dist/{p.name}"
data = {"title": meta["title"], "artist": meta["artist"], "versions": []}
for v in meta["versions"]:
    mp3 = dist / f"{meta['slug']}-{v['key']}.mp3"
    lyr = json.loads((dist / f"{v['key']}.lyrics.json").read_text())
    data["versions"].append({
        "key": v["key"], "label": v["label"], "size": f"{mp3.stat().st_size/1e6:.1f}MB",
        "mp3": ref(mp3, "audio/mpeg"), "cover": ref(dist / f"cover-{v['key']}.jpg", "image/jpeg"),
        "poster": ref(dist / f"poster-{v['key']}.jpg", "image/jpeg"),
        "lyrics": [{"sec": L["sec"], "text": L["text"], "t": L["t"]} for L in lyr],
    })
html = (Path(__file__).parent / "player.html").read_text()
html = (html.replace("__TITLE__", meta["title"]).replace("__ARTIST__", meta["artist"])
            .replace("__COLOR__", meta["color"]).replace("__DATA__", json.dumps(data, ensure_ascii=False)))
out = Path("work") / f"{meta['slug']}-preview.html" if single else song / "preview.html"
out.parent.mkdir(exist_ok=True); out.write_text(html)
print(out, f"{out.stat().st_size/1e6:.1f}MB")
