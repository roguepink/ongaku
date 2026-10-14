"""できた曲をホームページ(home-page)へ送る。
   python3 tools/export_to_home.py songs/<曲> [--draft]
   - 曲・ジャケットを home-page/public/music/<曲>/ へ
   - 曲の情報と歌詞の時刻を home-page/src/app/music/songs/<曲>.json へ
   --draft は試作: 一覧に出さず、検索にも出さない(アドレスを知っている人だけ見られる)"""
import json, shutil, sys
from pathlib import Path

song = Path(sys.argv[1]); draft = "--draft" in sys.argv
home = Path(__file__).resolve().parents[2] / "home-page"
meta = json.loads((song / "song.json").read_text())
slug = meta["slug"]
pub = home / "public" / "music" / slug
pub.mkdir(parents=True, exist_ok=True)
data = {"slug": slug, "title": meta["title"], "artist": meta["artist"], "color": meta["color"],
        "draft": draft, "versions": []}
for v in meta["versions"]:
    files = {"mp3": f"{slug}-{v['key']}.mp3", "cover": f"cover-{v['key']}.jpg", "poster": f"poster-{v['key']}.jpg"}
    for f in files.values(): shutil.copy(song / "dist" / f, pub / f)
    lyr = json.loads((song / "dist" / f"{v['key']}.lyrics.json").read_text())
    data["versions"].append({
        "key": v["key"], "label": v["label"], "created": v["created"],
        "size": f"{(song / 'dist' / files['mp3']).stat().st_size / 1e6:.1f}MB",
        **{k: f"/music/{slug}/{f}" for k, f in files.items()},
        "lyrics": lyr,
    })
out = home / "src" / "app" / "music" / "songs" / f"{slug}.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
print("→", pub, "\n→", out)
