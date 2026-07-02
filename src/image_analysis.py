import cv2
import numpy as np

class ImageAnalyzer:
    def __init__(self,image):
        self.image=image
        self.gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        self.height=self.image.shape[0]
        self.width=self.image.shape[1]
    
    def compute_brightness(self):
        brightness=np.mean(self.gray)
        return brightness
    
    def compute_contrast(self):
        contrast=np.std(self.gray) ##higher the std higher the contrast and vice versa ,to understand whether the pixels are wide spread or not.
        return contrast
    
    def compute_dynamic_range(self):
        dynamic_range=np.max(self.gray)-np.min(self.gray)
        return dynamic_range
    
    def compute_entropy(self):
        hist=self.compute_histogram()
        entropy=-np.sum(hist*np.log2(hist+1e-10))
        return entropy
    
    def estimate_noise(self):
        noise=cv2.Laplacian(self.gray,cv2.CV_64F).var()
        return noise
    def compute_histogram(self):
        hist=cv2.calcHist([self.gray],[0],None,[256],[0,256])
        hist=hist.flatten()
        hist=hist/hist.sum()
        return hist
    
    def compute_edge_density(self):
       edges = cv2.Canny(
        self.gray,
        100,
        200
    )

       return np.sum(
        edges > 0
    ) / edges.size
       
     
    def estimate_foreground_ratio(self):
     _, thresh = cv2.threshold(
        self.gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

     foreground = np.sum(thresh > 0)

     return foreground / thresh.size  
    
    
    def estimate_skin_variance(self):
     ycrcb = cv2.cvtColor(
        self.image,
        cv2.COLOR_BGR2YCrCb
    )

     cr = ycrcb[:, :, 1]

     cb = ycrcb[:, :, 2]

     mask = (
        (cr > 135) &
        (cr < 180) &
        (cb > 85) &
        (cb < 135)
    )

     if np.sum(mask) == 0:
        return 0

     return np.std(
        self.gray[mask]
    )
       
    def estimate_sharpness(self):
      return cv2.Laplacian(
        self.gray,
        cv2.CV_64F
    ).var()  
      
    def analyze(self):
        brightness=self.compute_brightness()
        contrast=self.compute_contrast()
        dynamic_range=self.compute_dynamic_range()
        entropy=self.compute_entropy()
        noise=self.estimate_noise()
        return {
            'brightness':brightness,
            'contrast':contrast,
            'dynamic_range':dynamic_range,
            'entropy':entropy,
            'noise':noise,
            'height':self.height,
            'width':self.width,
            'foreground_ratio':self.estimate_foreground_ratio(),
            'skin_variance':self.estimate_skin_variance(),
            'sharpness':self.estimate_sharpness(),
            'edge_density':self.compute_edge_density(),
            
            
            
        }
           