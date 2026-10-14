# ongaku — ノブさんの曲(Suno AI)の置き場

ノブさんのことは「ノブさん」と呼ぶ。日本語で、専門用語を避けて、要点を先に短く。

## このリポジトリは公開(public)
2026-10-14 ノブさんが「とりあえず公開で」と決めた。曲はダウンロードして聞いてもらうためのもの。
**映画の素材・顧客情報・健康情報・実在の人の写真は置かない。** 載せるジャケットは AI で作った絵だけ。
ホームページ(home-page)に載せるのは、**必ずノブさんに見せて OK をもらってから。**

## 1曲 = 1フォルダ `songs/<曲の名前(ローマ字)>/`
- `original/` … Suno から受け取ったままの mp3 と、ノブさんがくれた絵(さわらない)
- `song.json` … 曲名・名義・テーマ色・版(歌版/ラップ版など)
- `<版>.asr.json` … 機械が聞き取った歌(時刻つき)
- `dist/` … 配る用。mp3(音はそのまま。曲名・ジャケット・歌詞だけ入れ直し)、ジャケット、歌詞の時刻メモ
- `preview.html` … 試しのページ

## 手順(Mac で。`source ~/.local/venvs/ryokoshi/bin/activate`)
1. Suno の mp3 には歌詞が入っている(`[Intro - ...]` のような Suno への指示つき)。それをそのまま使う
2. 聞き取り: `tools/asr.py`(mlx-whisper large-v3-turbo、言葉ごとの時刻)
3. 歌詞と突き合わせ: `cd songs/<曲> && python3 ../../tools/align.py <版>...` → 一致率 95% 前後なら良好
   最後の「ご視聴ありがとうございました」は聞き間違いなので捨てている
4. 配る用: `python3 tools/make_dist.py songs/<曲>`(1曲 約5MB)
5. 試しのページ: `python3 tools/build_preview.py songs/<曲> [--single]`
   `--single` は曲も画像も1ファイルに入れた版(Mac で開く用、work/ にできる。GitHub には入れない)
   ※ このチャットからノブさんのスマホへファイルは送れない。見てもらうのはホームページの試作ページで
6. ホームページへ: `python3 tools/export_to_home.py songs/<曲> [--draft]`
   → home-page の `public/music/<曲>/` と `src/app/music/songs/<曲>.json` ができる。`src/app/music/songs.ts` の SONGS に足す
   → ブランチ → PR → Vercel が success → マージ。ページは `roguepink.com/music/<曲>`
   `--draft` は試作: 音楽の一覧に出さず、検索にも出さない

## ノブさんの決めたこと(2026-10-13〜14)
- ダウンロードは軽く(mp3、1曲 数MB)。動画はつけない。MV は頼まれた曲だけ別に作る
- ホームページの音楽ページは「音楽カード」と「MVカード」に分ける。音楽カードは音が主役で、歌詞は今歌っているところをなぞる
- ジャンルごとのまとまり(例: デスメタル、激しいBGM)に曲を並べたい。少ないジャンルは寂しく見えるので 3曲以上を目安に
- Suno はプロプラン(有料)
- 名義は「ROGUE PINK」(2026-10-14。Suno の名前 deathmaturi は使わない)
