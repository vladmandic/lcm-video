import sys
import cv2
from src.state import state
from src.logger import log

def video():
    def fourcc(cc):
        cc_bytes = int(cc).to_bytes(4, byteorder=sys.byteorder) # convert code to a bytearray
        cc_str = cc_bytes.decode() # decode byteaarray to a string
        return cc_str
    if state.input is None:
        log('error: video no input')
        state.started = False
        return None
    if state.stream is None:
        # state.stream = cv2.VideoCapture(0) # webcam
        state.stream = cv2.VideoCapture(state.input)
        if not state.stream.isOpened():
            log(f'error: video open failed: file={state.input}')
            state.started = False
            return None
        frames = int(state.stream.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(state.stream.get(cv2.CAP_PROP_FPS))
        w, h = int(state.stream.get(cv2.CAP_PROP_FRAME_WIDTH)), int(state.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = fourcc(state.stream.get(cv2.CAP_PROP_FOURCC))
        log(f'video: file="{state.input}" frames={frames} fps={fps} duration={frames / fps:.2f} resolution={w}x{h} codec={codec}')
    frame = None
    if state.stream is not None and state.started:
        _code, frame = state.stream.read()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame
