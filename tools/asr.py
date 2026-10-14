import mlx_whisper, json, sys
for name in ["rap","uta"]:
    r = mlx_whisper.transcribe(f"{name}.mp3", path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        language="ja", word_timestamps=True, condition_on_previous_text=False,
        initial_prompt="久しぶりに恋をした 黄色が好き ママへ")
    json.dump(r["segments"], open(f"{name}.asr.json","w"), ensure_ascii=False)
    for s in r["segments"]: print(name, round(s["start"],1), round(s["end"],1), s["text"])
