
import cv2
import numpy as np
from configparser import ConfigParser
import os
import imutils
import json
class figure_detection:
    def __init__(self):
        self.img_now = None
    
    def testDevice(source):
        cap = cv2.VideoCapture(source) 
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', source)
            return 0
        cap.release()
        return 1
        
       
    def increase_contrast(self, input_img, brightness = 0, contrast = 0):
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow

            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()

        if contrast != 0:
            f = 131*(contrast + 127)/(127*(131-contrast))
            alpha_c = f
            gamma_c = 127*(1-f)

            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

        return buf
            
    def main_loop(self, img, settings):
        # converting image into grayscale image
        settings_list = settings.get_params()
        self.SV_min = list(settings_list[0:2])
        self.SV_max = list(settings_list[2:4])
        self.area_min = settings_list[4]
        self.area_max = settings_list[5]
        open_kernel = settings_list[9]
        close_kernel = settings_list[10]
        image_out = img.copy()
        
        resized = img.copy()
        
        H_colors_range = settings.get_h_params()
        ##[
        ##    ["red", 155, 175],
        ##    ["green", 45, 65], 
        ##    ["blue", 90, 110]
        ##]
        
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        list_of_polygons = []
        for color in H_colors_range:
            thresh = cv2.inRange(hsv, np.array([int(color[1]), self.SV_min[0], self.SV_min[1]]),  np.array([int(color[2]), self.SV_max[0], self.SV_max[1]]))
            
            thresh = cv2.GaussianBlur(thresh, (5, 5), 0)
            kernel = np.ones((open_kernel,open_kernel),np.uint8)
            kernel1 = np.ones((close_kernel,close_kernel),np.uint8)

            thresh = cv2.morphologyEx(thresh.copy(), cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh.copy(), cv2.MORPH_CLOSE, kernel1)

            contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            contours = imutils.grab_contours(contours)
            
            for c in contours:
                c_area = cv2.contourArea(c)
                if(c_area < self.area_min or c_area > self.area_max):
                    continue

                cv2.drawContours(image_out, [c], 0, (0, 0, 255), 2)
                M = cv2.moments(c)
                if(M['m00'] != 0):
                    x = int(M['m10']/M['m00'])
                    y = int(M['m01']/M['m00'])
                
                    approx = cv2.approxPolyDP(c, 0.04 * cv2.arcLength(c, True), True)
                    edges_num = len(approx)
                
                    cv2.putText(image_out, str(edges_num) + " " + color[0], (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                    list_of_polygons.append([x,y,edges_num, c_area])
                
        
        settings.set_img(image_out)
                
        return image_out, list_of_polygons
        
class image_pipe:
    def __init__(self, path):
        self.path = path
        self.config = ConfigParser()
        self.config.read(path)
        
        self.ip = self.config.get('main', "ip")
        self.h_params = json.loads(self.config.get('main', 'h_params').replace("\'", "\""))
        self.settings = json.loads(self.config.get('main', 'settings').replace("\'", "\""))

        os.system("v4l2-ctl --set-ctrl=brightness=" + str(int(self.settings[6])))
        if(int(self.settings[7]) != 1):
            os.system("v4l2-ctl --set-ctrl=white_balance_automatic=0")
            os.system("v4l2-ctl --set-ctrl=white_balance_temperature=" + str(int(self.settings[7])))
        else:
            os.system("v4l2-ctl --set-ctrl=white_balance_automatic=1")
        os.system("v4l2-ctl --set-ctrl=contrast=" + str(int(self.settings[8])))
        self.h_params_now = list(self.h_params)
        self.settings_now = list(self.settings)
        
    def get_img_gener(self):
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + self.img + b'\r\n\r\n')
    def get_img(self):
        return self.img
    def set_img(self, img):
        self.img = img
    
    def get_ip(self):
        return self.ip
    def set_ip(self, ip):
        self.ip = str(ip)
    
    def get_h_params(self):
        return self.h_params_now
    def set_h_params(self, h_params):
        self.h_params_now = h_params
    
    def get_params(self):
        return self.settings_now
    def set_params(self, settings):
        self.settings_now = list(settings)

    def reset_params(self):
        self.settings_now = list(self.settings)
        self.h_params_now = list(self.h_params)
        
    def save_params(self):
        self.settings = list(self.settings_now)
        self.h_params = list(self.h_params_now)
        
        self.config.set('main', 'ip', str(self.ip))
        self.config.set('main', 'settings', str(self.settings))
        self.config.set('main', 'h_params', str(self.h_params))
        with open(self.path, "w") as config_file:
            self.config.write(config_file)
        config_file.close()
        
        
        

        
