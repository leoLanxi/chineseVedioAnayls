import os
from modelscope.hub.snapshot_download import snapshot_download

def main():
    cache = os.environ.get("MODELSCOPE_CACHE")
    if cache and os.path.isdir(cache):
        os.environ["MODELSCOPE_CACHE"] = cache
    snapshot_download("iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch")
    snapshot_download("iic/speech_fsmn_vad_zh-cn-16k-common-pytorch")
    snapshot_download("iic/punc_ct-transformer_cn-en-common-vocab471067-large")
    print("OK")

if __name__ == "__main__":
    main()

