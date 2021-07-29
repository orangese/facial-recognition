import sys
sys.path.insert(1, "../")

from facenet import FaceNet
from util.socket import WebSocket
from util.common import ON_CUDA, ON_JETSON


if __name__ == "__main__":
    detector = "trt-mtcnn" if ON_CUDA else "mtcnn"
    graphics = not ON_JETSON
    mtcnn_stride = 7 if ON_JETSON else 3
    resize = 1 if ON_JETSON else 0.6

    facenet = FaceNet()
    ws = WebSocket("10.56.9.186:8000", 1, facenet)
    ws.connect(detector=detector, graphics=graphics,
               mtcnn_stride=mtcnn_stride, resize=resize)
