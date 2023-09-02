import cv2
import threading
import time

class CameraCapture:
    def __init__(self, device=0, width=640, height=480, fps=30):
        ''' My encapsulated camera capture object '''
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        self.running = False

    def _gst_str(self):
        ''' Return a parameter string. Referenced from https://github.com/NVIDIA-AI-IOT/jetcam'''
        return 'nvarguscamerasrc sensor-id=%d ! video/x-raw(memory:NVMM), width=%d, height=%d, format=(string)NV12, framerate=(fraction)%d/1 ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! videoconvert ! appsink' % (
                self._device, self._width, self._height, self._fps, self._width, self._height)

    def Live_start(self):
        ''' Init the camera with live read (read the latest frame) mode. '''
        self.running = True

        self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise Exception('Camera open failed!')
        
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def _capture_frames(self):   
        while self.running:
            # Use grab() to capture the next frame (non-blocking)
            success = self.cap.grab()
            if not success:
                print('`_capture_frames()` exited unexpectedly since self.cap.grab() return False. ')
                break
            time.sleep(0.8 / self._fps) # don't need to call so frequently!
        
    def Live_stop(self):
        ''' Stop the camera with live read mode.'''
        self.running = False
        self.capture_thread.join()
        self.cap.release()
        delattr(self, 'cap')

    def Live_read(self, nocopy=True):
        ''' Live-read frames. It will get the **latest** frame. 
            Require calling after `Live_start`. 
        '''
        if not self.running:
            raise Exception('`Live_read` should be called after camera.Live_start()!!!')

        # Use retrieve() to decode and retrieve the last grabbed frame
        ret, frame = self.cap.retrieve()

        if ret:
            return True, frame if nocopy else frame.copy()
        else:
            return False, None
  
    def Buffer_read(self):
        ''' Read oldest frame in the buffer. In the first time, it will create the cap object.

            Note that read will just fetch one **oldest frame** in the buffer. The buffer may
            overflow. If you want to get the newest frame, consider use `Live_read`. 
        '''
        if self.running:
            raise Exception('Cannot call `sync_read` in async mode. ')
        if not hasattr(self, 'cap'):
            self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)
        return self.cap.read()
    
    def Buffer_stop(self):
        ''' Stop the camera resources.'''
        self.cap.release()
        delattr(self, 'cap')

    def self_check(self):
        ''' Check if the camera can retrieve images correctly '''
        self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)
        for _ in range(10):
            ret, _ = self.cap.read()
            if ret:
                print('[SELF CHECK] : Self check succeed!')
                self.Buffer_stop()
                return True
        print('[SELF CHECK] : Self check failed! Consider reboot the machine. ')
        self.Buffer_stop()
        return False
    