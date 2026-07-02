import cv2
import numpy as np

class ColorQuantizer:
    def __init__(self,image,stats):
        self.image=image
        self.stats=stats
        
    
    def automatic_k_selection(self):
     entropy = self.stats["entropy"]
     
     if entropy < 5.5:
        return 8

     elif entropy < 6.5:
        return 10

     else:
        return 12
    
    
    def should_mean_shift(self):
        return (self.stats['entropy']>7.0 and self.stats['edge_density']<0.08)
    
    def mean_shift(self,image):
         return cv2.pyrMeanShiftFiltering(image,sp=8,sr=12)
    
    def kmeans_quantization(self,image,k:int=8):
        pixels=image.reshape(-1,3)
        pixels=np.float32(pixels)
        k=self.automatic_k_selection()
        criteria=(
            cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,
            50,
            0.2
        )
        _,labels,center=cv2.kmeans(pixels,k,None,criteria,10,cv2.KMEANS_PP_CENTERS)
        center=np.uint8(center)
        color_quantized=center[labels.flatten()]
        color_quantized=color_quantized.reshape(image.shape)
        return color_quantized
    
    
    def get_bilateral_iterations(self):

     noise = self.stats["noise"]

     if noise < 200:
        return 1

     elif noise < 500:
        return 2
     else:  
      return 3
        
    def bilateral_filter(self,diameter:int=7,sigma_color:int=40,sigma_space:int=40,iterations:int=3):
        iterations=self.get_bilateral_iterations()
        image=self.image.copy()
        for _ in range(iterations):
            image=cv2.bilateralFilter(image,diameter,sigma_color,sigma_space)
        
        return image    
    
    def detail_reinjection(self,original,quantized,alpha:float=0.15):
         detail = cv2.subtract(
            original,
            quantized       
        )

         result = cv2.addWeighted(
            quantized,
            1.0,
            detail,
            alpha,
            0
        )

         return result 
     
    def preserve_skin(self, original, quantized):

     mask = cv2.cvtColor(
        original,
        cv2.COLOR_BGR2YCrCb
    )

     lower = np.array([0,135,85])
     upper = np.array([255,180,135])

     skin_mask = cv2.inRange(
        mask,
        lower,
        upper
    )

     skin_mask = cv2.GaussianBlur(
        skin_mask,
        (5,5),
        0
    )

     skin_mask = skin_mask.astype(np.float32)/255.0
     skin_mask = cv2.merge(
        [skin_mask]*3
    )

     result = (
        quantized*(1-skin_mask)
        +
        original*skin_mask*0.55
        +
        quantized*skin_mask*0.45
    )

     return result.astype(np.uint8)    
     
    def quantize(self):

        smooth = self.bilateral_filter()

        if self.should_mean_shift() :
            smooth = self.mean_shift(
                smooth
            )

        lab=cv2.cvtColor(smooth,cv2.COLOR_BGR2LAB)
        quantized = self.kmeans_quantization(
            lab
        )
        quantized=cv2.cvtColor(quantized,cv2.COLOR_LAB2BGR)

      
        quantized = self.detail_reinjection(
                self.image,
                quantized,
                alpha=0.15
            )
        quantized=self.preserve_skin(self.image,quantized)
        quantized = cv2.bilateralFilter(
        quantized,
        5,
        20,
        20
    )

        return quantized
         