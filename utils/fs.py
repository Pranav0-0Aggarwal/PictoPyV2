import os
import hashlib
from typing import Generator

def genHash(imgPath: str) -> str:
    with open(imgPath, "rb") as f:
        imgData = f.read()
        return hashlib.md5(imgData).hexdigest()

def isImg(filePath: str) -> bool:
    _, fileExtension = os.path.splitext(filePath)
    imgExts = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".avif"]
    return fileExtension.lower() in imgExts

def imgPaths(startPath: str) -> Generator[str, None, None]:
    for root, dirs, files in os.walk(startPath):
        for file in files:
            if isImg(file):
                yield os.path.join(root, file)
