"""
This class is used to initialize the camera, and subsequently 
take pictures, then return values for min and max of difference
between images.


To use:
>> import snp
>> mycam = snp.snapper()      ; Create instance
>> mycam.setup()              ; Initialize the camera
>> mycam.blank()              ; Take the reference image
>> thing = mycam.curnt()      ; Take subsequent images; 
                                min/max values reuturned
>> mycam.clser()              ; Close, release camera



"""

import cv2
import numpy as np

class snapper:
    def __init__(self):
        self.counter = 0
        
        
    def setup(self):
        """
        Initialize the USB cam (usually takes ~10s)
        """
        self.cam = cv2.VideoCapture(0)
        print('Camera Initialized!!!') 
        cv2.namedWindow("test")
        
        
    def blank(self):
        """
        Create 'blank' reference image (no puck)
        """
        ret1, self.blnk = self.cam.read()
        if not ret1:
            print("failed to grab frame")
        else:
            img_name1 = "blankimg.png"
            cv2.imwrite(img_name1, self.blnk)
            self.imgBK = cv2.cvtColor(self.blnk, cv2.COLOR_BGR2GRAY)
            print("{} written!".format(img_name1))
            #cv2.imshow("Blank image", self.blnk)
    
    def curnt(self):
        """
        Take each reference image, save the .png file
        """
        ret2, self.frame = self.cam.read()
        
        if not ret2:
            print("failed to grab frame")
        else:
            self.imgGS = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            subt = cv2.subtract(self.imgBK, self.imgGS)
            #cv2.imshow('this img',subt)
           
            indices = np.where(np.logical_and(subt > 150, subt < 255))
            x_vals = indices[1]
            y_vals = indices[0]
            try:
                xmin = min(x_vals)
                xmax = max(x_vals)
                ymin = min(y_vals)
                ymax = max(y_vals)
                img_name2 = "opencv_frame_{}.png".format(self.counter)
                cv2.imwrite(img_name2, self.frame)
                #print("{} written!".format(img_name2))
                self.counter += 1
                return xmin,xmax,ymin,ymax
            
            except ValueError:
               
                xmin = -1
                xmax = -1
                ymin = -1
                ymax = -1
                
        
        
    def clser(self):
        """
        Close camera and release
        """
        self.cam.release()
        cv2.destroyAllWindows()
        
# if __name__=="__main__":
#     import snp
#     import time
#     mycam = snp.snapper()
#     mycam.setup()
#     mycam.blank()
#     time.sleep(10)
#     thing = mycam.curnt()
#     print('took pic')
#     mycam.clser() 
    

