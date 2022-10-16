import sys
import cv2
import xml.etree.ElementTree as ET
from pathlib import Path
import math
import numpy as np

"""
rect = cv2.minAreaRect(cnt)
box = cv2.cv.BoxPoints(rect) # cv2.boxPoints(rect) for OpenCV 3.x
box = np.int0(box)
cv2.drawContours(im,[box],0,(0,0,255),2)
"""


def parse_xml(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    size = root.find("size")
    width = int(size.find("width").text)
    height = int(size.find("height").text)
    boxes = []
    for obj in root.iter("object"):
        xmlbox = obj.find("robndbox")
        cx = float(xmlbox.find("cx").text)
        cy = float(xmlbox.find("cy").text)
        w = float(xmlbox.find("w").text)
        h = float(xmlbox.find("h").text)
        angle = float(xmlbox.find("angle").text)
        name = obj.find("name").text
        # if w < h:
        if False:
            w, h = h, w
            # theta = int(((theta * 180 / math.pi) + 90) % 180)
        else:
            # theta = int(theta * 180 / math.pi)
            pass
        x1 = cx + (w / 2) * math.cos(angle) - (h / 2) * math.sin(angle)
        y1 = cy + (w / 2) * math.sin(angle) + (h / 2) * math.cos(angle)
        x2 = cx - (w / 2) * math.cos(angle) - (h / 2) * math.sin(angle)
        y2 = cy - (w / 2) * math.sin(angle) + (h / 2) * math.cos(angle)
        x3 = cx - (w / 2) * math.cos(angle) + (h / 2) * math.sin(angle)
        y3 = cy - (w / 2) * math.sin(angle) - (h / 2) * math.cos(angle)
        x4 = cx + (w / 2) * math.cos(angle) + (h / 2) * math.sin(angle)
        y4 = cy + (w / 2) * math.sin(angle) - (h / 2) * math.cos(angle)
        boxes.append([(x1, y1), (x2, y2), (x3, y3), (x4, y4), name])
        # break
    return boxes


def parse_txt(txt):
    entries = txt.read().splitlines()
    boxes = []
    for entry in entries:
        sp = entry.split()
        if len(sp) < 9:
            continue
        b = [float(v) for v in sp[:8]]
        boxes.append([(b[0], b[1]), (b[2], b[3]), (b[4], b[5]), (b[6], b[7]), sp[8]])
    return boxes


def show_obb(image: Path, anno: Path):
    if anno.suffix == ".xml":
        boxes = parse_xml(open(anno))
    if anno.suffix == ".txt":
        boxes = parse_txt(open(anno))

    img = cv2.imread(str(image))
    w, h = img.shape[1], img.shape[0]
    maxlen = max(w, h)
    thickness = maxlen // 500
    for box in boxes:
        box = np.array(box[:4], np.int32)
        cv2.polylines(img, [box], isClosed=True, color=(0, 255, 0), thickness=thickness)
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--image", required=True)
    parser.add_argument("--anno", required=True)
    args = parser.parse_args()

    show_obb(Path(args.image), Path(args.anno))
