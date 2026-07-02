import cv2
import numpy as np

class PostProcessor:
    def __init__(self,cartoon):
        self.cartoon=cartoon
   
    def increase_saturation(self, image, factor=1.15):
     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

     hsv[:, :, 1] = np.clip(
        hsv[:, :, 1] * factor,
        0,
        255
    )

     return cv2.cvtColor(
        hsv.astype(np.uint8),
        cv2.COLOR_HSV2BGR
    )
    
    def increase_contrast(self, image,
                      alpha=1.05,
                      beta=3):

     return cv2.convertScaleAbs(
        image,
        alpha=alpha,
        beta=beta
    )
     
    def soften(self, image):

      return cv2.bilateralFilter(
        image,
        5,
        20,
        20
    )
      
    def sharpen(self, image):
          blur=cv2.GaussianBlur(image,(0,0),2)
          return cv2.addWeighted(image,1.3,blur,-0.3,0)
        
    def add_skin_tone(self,image):
        tone=cv2.GaussianBlur(
            image,
            (0,0),
            5
        )
        return cv2.addWeighted(image,0.85,tone,0.15,0)
     
    def process(self):
        cartoon=self.cartoon.copy()
       

        cartoon = self.increase_saturation(
            cartoon
        )

        cartoon = self.increase_contrast(
            cartoon
        )

        cartoon = self.soften(cartoon)
        cartoon=self.add_skin_tone(cartoon)

        cartoon = self.sharpen(cartoon)

        return cartoon