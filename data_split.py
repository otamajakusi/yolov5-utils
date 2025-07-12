import glob
import os
import random
import re
from pathlib import Path


def get_ext(basename, exts=["jpg", "png"]):
    for ext in exts:
        if Path(basename).with_suffix(f".{ext.upper()}").exists():
            return ext.upper()
        if Path(basename).with_suffix(f".{ext.lower()}").exists():
            return ext.lower()
    return None


def split_data(dataset_path, out_path, percentage_test=20):
    # Populate the folders
    p = percentage_test / 100

    out_path = Path(out_path)
    (out_path / "images" / "valid").mkdir(parents=True, exist_ok=True)
    (out_path / "labels" / "valid").mkdir(parents=True, exist_ok=True)
    (out_path / "images" / "train").mkdir(parents=True, exist_ok=True)
    (out_path / "labels" / "train").mkdir(parents=True, exist_ok=True)

    dataset_path = Path(dataset_path)
    pa = re.compile(r"\.txt$", re.IGNORECASE)
    for path in dataset_path.rglob("*"):
        if not path.is_file() or not pa.search(path.name):
            continue
        base_path = path.parent / path.stem
        ext = get_ext(base_path)
        if ext is None:
            print(f"WARN: image not found for {path}")
            continue
        if random.random() <= p:
            os.system(f"cp {str(base_path)}.{ext} {out_path}/images/valid")
            os.system(f"cp {str(path)} {out_path}/labels/valid")
        else:
            os.system(f"cp {str(base_path)}.{ext} {out_path}/images/train")
            os.system(f"cp {str(path)} {out_path}/labels/train")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath", required=True, help="dataset path")
    parser.add_argument("--outpath", required=True, help="output path")
    args = parser.parse_args()
    split_data(args.datapath, args.outpath)
