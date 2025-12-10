import os
import sys
import json
import tempfile
from typing import List, Dict, Any
from cn_asr.formatter import clean_zh_text, split_sentences, group_paragraphs, build_srt_content

def ensure_dir(p: str) -> None:
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)

def list_videos(root: str) -> List[str]:
    exts = {".mp4", ".mov", ".mkv", ".avi", ".mp3", ".wav", ".m4a"}
    r = []
    if not os.path.isdir(root):
        return r
    for dirpath, _, filenames in os.walk(root):
        for n in sorted(filenames):
            e = os.path.splitext(n)[1].lower()
            if e in exts:
                r.append(os.path.join(dirpath, n))
    return r

def extract_audio(video_path: str, tmp_dir: str) -> str:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    n = os.path.splitext(os.path.basename(video_path))[0]
    out = os.path.join(tmp_dir, n + ".wav")
    try:
        clip = VideoFileClip(video_path)
        if clip.audio is None:
            raise RuntimeError("no_audio")
        clip.audio.write_audiofile(out, fps=16000, nbytes=2, codec="pcm_s16le")
        clip.close()
    except Exception:
        try:
            a = AudioFileClip(video_path)
            a.write_audiofile(out, fps=16000, nbytes=2, codec="pcm_s16le")
            a.close()
        except Exception as e:
            raise e
    return out

def asr_with_funasr(wav_path: str) -> List[Dict[str, Any]]:
    from funasr import AutoModel
    m = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc", disable_update=True)
    res = m.generate(input=wav_path, batch_size=1)
    items = []
    for r in res:
        tx = r.get("text", "")
        st = int(float(r.get("start", 0)) * 1000) if "start" in r else None
        et = int(float(r.get("end", 0)) * 1000) if "end" in r else None
        ts = r.get("timestamp") or r.get("time_stamp")
        if ts and isinstance(ts, list):
            try:
                if ts and isinstance(ts[0], (list, tuple)):
                    st = int(float(ts[0][0]) * 1000)
                    et = int(float(ts[-1][1]) * 1000)
                elif len(ts) >= 2:
                    st = int(float(ts[0]) * 1000)
                    et = int(float(ts[1]) * 1000)
            except Exception:
                pass
        items.append({"start": st, "end": et, "text": tx})
    return items

def refine_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    r = []
    for s in segments:
        tx = clean_zh_text(s.get("text", ""))
        if not tx:
            continue
        st = s.get("start")
        et = s.get("end")
        r.append({"start": st, "end": et, "text": tx})
    return r

def split_by_sentences_with_time(seg: Dict[str, Any]) -> List[Dict[str, Any]]:
    st = seg.get("start")
    et = seg.get("end")
    tx = seg.get("text", "")
    if st is None or et is None or et <= st:
        ss = split_sentences(tx)
        return [{"start": None, "end": None, "text": s} for s in ss] if ss else [{"start": None, "end": None, "text": tx}]
    ss = split_sentences(tx)
    if len(ss) <= 1:
        return [{"start": st, "end": et, "text": tx}]
    total = len(tx)
    cur = st
    r = []
    for s in ss:
        frac = len(s) / total if total > 0 else 1.0
        dur = int((et - st) * frac)
        ns = cur
        ne = ns + max(dur, 500)
        if ne > et:
            ne = et
        r.append({"start": ns, "end": ne, "text": s})
        cur = ne
    if r:
        r[-1]["end"] = et
    return r

def get_wav_duration_ms(wav_path: str) -> int:
    import wave
    with wave.open(wav_path, "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        dur = int(frames * 1000 / max(rate, 1))
    return dur

def allocate_times(sent_texts: List[str], total_ms: int) -> List[Dict[str, Any]]:
    if not sent_texts:
        return []
    weights = [max(len(s), 6) for s in sent_texts]
    total_w = sum(weights)
    min_ms = 1200
    remain = max(total_ms - min_ms * len(sent_texts), 0)
    cur = 0
    r = []
    for i, s in enumerate(sent_texts):
        base = min_ms
        extra = int(remain * (weights[i] / total_w)) if total_w > 0 else 0
        dur = base + extra
        st = cur
        et = st + dur
        r.append({"start": st, "end": et, "text": s})
        cur = et
    if r:
        r[-1]["end"] = max(r[-1]["end"], total_ms)
    return r

def build_outputs_for_video(video_path: str, out_dir: str) -> None:
    ensure_dir(out_dir)
    name = os.path.splitext(os.path.basename(video_path))[0]
    subdir = os.path.join(out_dir, name)
    ensure_dir(subdir)
    with tempfile.TemporaryDirectory() as tmp:
        wav = extract_audio(video_path, tmp)
        raw = asr_with_funasr(wav)
        segs = refine_segments(raw)
        sents = []
        for s in segs:
            sents.extend(split_by_sentences_with_time(s))
        sent_texts = [it.get("text", "") for it in sents if it.get("text")]
        srt_items = []
        for it in sents:
            if it.get("start") is None or it.get("end") is None:
                continue
            srt_items.append((it["start"], it["end"], it["text"]))
        if not srt_items and sent_texts:
            total_ms = get_wav_duration_ms(wav)
            alloc = allocate_times(sent_texts, total_ms)
            srt_items = [(x["start"], x["end"], x["text"]) for x in alloc]
        srt_txt = build_srt_content(srt_items)
        paras = group_paragraphs(sent_texts, 120)
        from docx import Document
        doc = Document()
        for p in paras:
            doc.add_paragraph(p)
        srt_path = os.path.join(subdir, name + ".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_txt)
        docx_path = os.path.join(subdir, name + ".docx")
        doc.save(docx_path)

def main() -> None:
    root = os.path.join(os.getcwd(), "input_videos")
    out_dir = os.path.join(os.getcwd(), "outputs")
    ensure_dir(out_dir)
    ensure_dir(root)
    vids = list_videos(root)
    for v in vids:
        try:
            build_outputs_for_video(v, out_dir)
            print(f"完成: {os.path.basename(v)} -> outputs/{os.path.splitext(os.path.basename(v))[0]}/")
        except Exception as e:
            print(f"处理失败: {v}: {e}", file=sys.stderr)
    if not vids:
        print(f"未在 {root} 找到可处理的视频文件。支持: mp4/mov/mkv/avi/mp3/wav/m4a", file=sys.stderr)

if __name__ == "__main__":
    main()
