import cv2
import numpy as np
from aruco_detection import aruco_detection
import numpy as np
from figure_detection import figure_detection, image_pipe
from webpage import web_interface
from multiprocessing import Queue, Process, Pipe, Manager
from multiprocessing.managers import BaseManager
import pyshine as ps
import time
import socket
import serial
import json

cam_index = 0
settings_file_path = 'config.ini'
def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

def video_feed(inst):
    server_ip = inst.get_ip()
    port = 5001
    HTML="""
    <html>
    <body>
    <center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center>
    </body>
    </html>
    """
    address = (server_ip,port)
    StreamProps = ps.StreamProps
    StreamProps.set_Page(StreamProps,HTML)
    StreamProps.set_Mode(StreamProps,'cv2')
    StreamProps.set_Capture(StreamProps,inst )
    StreamProps.set_Quality(StreamProps,90)
    server = ps.Streamer(address,StreamProps)

    print('Server started at','http://'+address[0]+':'+str(address[1]))
    server.serve_forever()
if __name__ == '__main__':
    local_ip = get_local_ip()

    BaseManager.register('image_pipe', image_pipe)
    manager = BaseManager()
    manager.start()
    inst = manager.image_pipe(settings_file_path)

    inst.set_ip(local_ip)

    cap = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)
    fig_det = figure_detection()
    aruco_det = aruco_detection()
    

    web_proc = Process(target=web_interface, args=(inst,))

    web_proc.start()
    count = 0
    frame_rate = 5
    prev = 0

    video_proc = Process(target=video_feed, args=(inst,))
    video_proc.start()
    
    ser = serial.Serial('/dev/ttyS1', 9600)
    
    while True:

        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            prev = time.time()
            ret, img = cap.read()
            if(inst.get_params()[11] == 0):
                ##sorry for the crazy mode, they forced me
                ##here is the normal transmission
                img, dat = fig_det.main_loop(img, inst)
                ##ser.write(str(dat).encode() + "\n".encode())
                is_find = False
                for i in dat:
                    if(i[2] == 10):
                        is_find = True
                        if(i[3] > 5000):
                            ser.write("back\n".encode())
                        elif(i[3] < 4000):
                            ser.write("forward\n".encode())
                        elif(i[0] < 250):
                            ser.write("left\n".encode())
                        elif(i[0] > 390):
                            ser.write("right\n".encode())
                        else:
                            ser.write("stop\n".encode())
                if(not is_find):
                    ser.write("stop\n".encode())
            else:
            	img, dat = aruco_det.main_loop(img,inst)
            	ser.write(str(list(map(lambda x: [int(x[0]), list(map(lambda y: [int(y[0]),int(y[1])], x[1]))],dat))).encode() + "\n".encode())


