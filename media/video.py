import cv2
from yolov8 import detectClasses

def extractFrames(inputPath, skip = 6):
    cap = cv2.VideoCapture(inputPath)
    frameCount = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frameCount % skip == 0:
            yield frame
        frameCount += 1
    cap.release()

def processFrames(frames, modelPath):
    frameClasses = []
    for frame in frames:
        yield detectClasses(frame, modelPath)

def saveVideo(outputPath, frames, fps, frameSize):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(outputPath, fourcc, fps, frameSize)
    for frame in frames:
        out.write(frame)
    out.release()

def videoClasses(inputPath, modelPath, outputPath=None):
    frames = extractFrames(inputPath)
    fps = cv2.VideoCapture(inputPath).get(cv2.CAP_PROP_FPS)
    firstFrameClasses, firstFrame = next(processFrames(frames, modelPath))

    def combinedFrames():
        yield firstFrame
        for _, frame in processFrames(frames, modelPath):
            yield frame

    if outputPath:
        height, width, _ = firstFrame.shape
        frameSize = (width, height)

        # Save the first frame and the rest of the processed frames
        saveVideo(outputPath, combinedFrames(), fps, frameSize)

    # Collect and return combined classes from each and every frame of the video
    allClasses = set(firstFrameClasses)
    for _, classes in processFrames(frames, modelPath):
        allClasses.update(classes)
    
    return allClasses
