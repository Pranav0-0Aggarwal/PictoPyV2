import cv2
import numpy as np
from typing import List, Tuple
from yolov8.YOLOv8 import detectClasses

def saveImage(image: cv2.Mat, filename: str) -> None:
    """
    Save an image to a file.

    Args:
        image (cv2.Mat): The image to save.
        filename (str): The path to the output file.
    """
    cv2.imwrite(filename, image)

def imageClasses(imgPath: str, model_path: str, outputPath: str = None) -> List[str]:
    img = cv2.imread(imgPath)
    if outputPath:
        saveImage(detectClasses(img, model_path)[1], outputPath)
    return detectClasses(img, model_path)[0]
    