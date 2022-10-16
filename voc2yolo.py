# https://zhuanlan.zhihu.com/p/391137600
import xml.etree.ElementTree as ET
import math
import glob
from pathlib import Path
from pprint import pprint


def convert_bndbox(size, xmlbox, cls_id):

    b = (
        float(xmlbox.find("xmin").text),
        float(xmlbox.find("xmax").text),
        float(xmlbox.find("ymin").text),
        float(xmlbox.find("ymax").text),
    )
    b1, b2, b3, b4 = b

    if b2 > w:
        b2 = w
    if b4 > h:
        b4 = h
    b = (b1, b2, b3, b4)

    def convert(size, box):
        dw = 1.0 / (size[0])
        dh = 1.0 / (size[1])
        x = (box[0] + box[1]) / 2.0 - 1
        y = (box[2] + box[3]) / 2.0 - 1
        w = box[1] - box[0]
        h = box[3] - box[2]
        x = x * dw
        w = w * dw
        y = y * dh
        h = h * dh
        return x, y, w, h

    bb = convert((w, h), b)
    return f'{cls_id} {" ".join([str(a) for a in bb])}\n'


def convert_robndbox(size, xmlbox, name):
    cx, cy, w, h = (
        float(xmlbox.find("cx").text),
        float(xmlbox.find("cy").text),
        float(xmlbox.find("w").text),
        float(xmlbox.find("h").text),
    )
    angle = float(xmlbox.find("angle").text)

    x1 = cx + (w / 2) * math.cos(angle) - (h / 2) * math.sin(angle)
    y1 = cy + (w / 2) * math.sin(angle) + (h / 2) * math.cos(angle)
    x2 = cx - (w / 2) * math.cos(angle) - (h / 2) * math.sin(angle)
    y2 = cy - (w / 2) * math.sin(angle) + (h / 2) * math.cos(angle)
    x3 = cx - (w / 2) * math.cos(angle) + (h / 2) * math.sin(angle)
    y3 = cy - (w / 2) * math.sin(angle) - (h / 2) * math.cos(angle)
    x4 = cx + (w / 2) * math.cos(angle) + (h / 2) * math.sin(angle)
    y4 = cy + (w / 2) * math.sin(angle) - (h / 2) * math.cos(angle)

    # https://github.com/otamajakusi/yolov5_obb/blob/master/docs/GetStart.md

    return f"{x1} {y1} {x2} {y2} {x3} {y3} {x4} {y4} {name} 0\n"


def convert_annotation(xml, classes):
    tree = ET.parse(xml)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)
    yolo = ""
    for obj in root.iter("object"):
        difficult = obj.find("difficult").text
        cls = obj.find("name").text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)

        while True:
            xmlbox = obj.find("robndbox")
            if xmlbox:
                yolo += convert_robndbox((w, h), xmlbox, cls)
                break

            xmlbox = obj.find("bndbox")
            if xmlbox:
                yolo += convert_bndbox((w, h), xmlbox, cls_id)
                break

            print("WARN: neither robndbox nor bndbox was found")
            break
    return yolo


def voc2yolo(path: Path, class_file):
    if path.is_dir():
        xmls = [Path(f) for f in glob.glob(f"{path}/*.xml")]
    else:
        xmls = [path]
    classes = open(class_file).read().splitlines()
    for xml in xmls:
        with open(xml) as in_file:
            yolo = convert_annotation(in_file, classes)
            with open(f"{xml.parent / xml.stem}.txt", "w") as out_file:
                out_file.write(yolo)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--path", required=True)
    parser.add_argument("--class-file", required=True)
    args = parser.parse_args()

    voc2yolo(Path(args.path), args.class_file)
