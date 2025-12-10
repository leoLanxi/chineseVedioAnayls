import sys, os
sys.path.insert(0, os.getcwd())
from cn_asr.formatter import clean_zh_text, split_sentences, group_paragraphs, build_srt_content

def run() -> None:
    t = "然后然后我我我就去那边了，然后就看到了。啊啊啊，那个那个挺好的！"
    c = clean_zh_text(t)
    sents = split_sentences(c)
    paras = group_paragraphs(sents, 40)
    items = [(0, 1800, sents[0]), (2000, 3800, sents[1])]
    srt = build_srt_content(items)
    print("CLEAN:", c)
    print("SENTS:", sents)
    print("PARAS:", paras)
    print("SRT:\n" + srt)

if __name__ == "__main__":
    run()
