import os
import time
import cv2
import numpy as np
import onnxruntime

from utils import xywh2xyxy, draw_detections, multiclass_nms, class_names


class YOLOv8:

    def __init__(self, path, conf_thres=0.7, iou_thres=0.5):
        self.conf_threshold = conf_thres
        self.iou_threshold = iou_thres

        # Initialize model
        self.initialize_model(path)

    def __call__(self, image):
        return self.detect_objects(image)

    def initialize_model(self, path):
        self.session = onnxruntime.InferenceSession(path,
                                                    providers=onnxruntime.get_available_providers())
        # Get model info
        self.get_input_details()
        self.get_output_details()


    def detect_objects(self, image):
        input_tensor = self.prepare_input(image)

        # Perform inference on the image
        outputs = self.inference(input_tensor)

        self.boxes, self.scores, self.class_ids = self.process_output(outputs)

        return self.boxes, self.scores, self.class_ids

    def prepare_input(self, image):
        self.img_height, self.img_width = image.shape[:2]

        input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize input image
        input_img = cv2.resize(input_img, (self.input_width, self.input_height))

        # Scale input pixel values to 0 to 1
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)

        return input_tensor


    def inference(self, input_tensor):
        start = time.perf_counter()
        outputs = self.session.run(self.output_names, {self.input_names[0]: input_tensor})

        # print(f"Inference time: {(time.perf_counter() - start)*1000:.2f} ms")
        return outputs

    def process_output(self, output):
        predictions = np.squeeze(output[0]).T

        # Filter out object confidence scores below threshold
        scores = np.max(predictions[:, 4:], axis=1)
        predictions = predictions[scores > self.conf_threshold, :]
        scores = scores[scores > self.conf_threshold]

        if len(scores) == 0:
            return [], [], []

        # Get the class with the highest confidence
        class_ids = np.argmax(predictions[:, 4:], axis=1)

        # Get bounding boxes for each object
        boxes = self.extract_boxes(predictions)

        # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
        # indices = nms(boxes, scores, self.iou_threshold)
        indices = multiclass_nms(boxes, scores, class_ids, self.iou_threshold)

        return boxes[indices], scores[indices], class_ids[indices]

    def extract_boxes(self, predictions):
        # Extract boxes from predictions
        boxes = predictions[:, :4]

        # Scale boxes to original image dimensions
        boxes = self.rescale_boxes(boxes)

        # Convert boxes to xyxy format
        boxes = xywh2xyxy(boxes)

        return boxes

    def rescale_boxes(self, boxes):

        # Rescale boxes to original image dimensions
        input_shape = np.array([self.input_width, self.input_height, self.input_width, self.input_height])
        boxes = np.divide(boxes, input_shape, dtype=np.float32)
        boxes *= np.array([self.img_width, self.img_height, self.img_width, self.img_height])
        return boxes

    def draw_detections(self, image, draw_scores=True, mask_alpha=0.4):

        return draw_detections(image, self.boxes, self.scores,
                               self.class_ids, mask_alpha)

    def get_input_details(self):
        model_inputs = self.session.get_inputs()
        self.input_names = [model_inputs[i].name for i in range(len(model_inputs))]

        self.input_shape = model_inputs[0].shape
        self.input_height = self.input_shape[2]
        self.input_width = self.input_shape[3]

    def get_output_details(self):
        model_outputs = self.session.get_outputs()
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]


def markObjects(url, model_path, conf_thres=0.3, iou_thres=0.5):
    img = cv2.imread(url)
    yolov8_detector = YOLOv8(model_path, conf_thres, iou_thres)

    # Detect Objects
    boxes, scores, class_ids = yolov8_detector.detect_objects(img)

    # Optionally, draw detections and save the image again
    img = yolov8_detector.draw_detections(img)

    return img, boxes, scores, class_ids

def save_image(image, filename):
    cv2.imwrite(filename, image)


def prepend_to_file(folder_name, file_path):
    """
    Prepend a folder name to the path of a file before the filename.

    Args:
        folder_name (str): The name of the folder to prepend.
        file_path (str): The original path to the file.

    Returns:
        str: The modified path with the folder name prepended.
    """
    # Extract the base name (filename) from the file path
    base_name = os.path.basename(file_path)
    
    # Remove the base name from the file path to get the directory path
    dir_path = os.path.dirname(file_path)
    
    # Join the directory path with the folder name and the base name
    new_path = os.path.join(dir_path, folder_name, base_name)
    
    return new_path


def saveOutputImage(imgPath, img_with_detections):
    outputPath = prepend_to_file("output", imgPath)
    save_image(img_with_detections, outputPath)

def uniqueClasses(class_ids):
    classes = []
    for id in np.unique(class_ids):
        classes.append(class_names[id])
    return classes

def detectedClass(imgPath):
    model_path = "models/yolov8n.onnx"
    img_with_detections, boxes, scores, class_ids = load_and_process_image(imgPath, model_path)
    saveOutputImage(imgPath, img_with_detections)
    return uniqueClasses(class_ids)



print(detectedClass("../.images/image.jpg"))