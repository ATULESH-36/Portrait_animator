import cv2
import numpy as  np
from src.image_analysis import ImageAnalyzer
class ImagePreProcessor:
    def __init__(self,image,stats):
        self.image=image
        self.stats=stats
    
    def resize(self,image,max_dimension=720)->np.ndarray:
        h,w=image.shape[:2]
        largest_dimension=max(h,w)
        
        if largest_dimension>max_dimension:
            scale=max_dimension/largest_dimension
            nw=int(w*scale)
            nh=int(h*scale)
            resized_image=cv2.resize(image,(nw,nh),interpolation=cv2.INTER_AREA)
            return resized_image
        else:
            return image
    
    def gamma_correction(self,image:np.ndarray,gamma:float)->np.ndarray:
        
        if gamma<=0:
            raise ValueError("gamma must be positive")
        inv_gamma=1.0/gamma
        table=np.array([((i/255.0)**inv_gamma)*255 for i in np.arange(0,256)]).astype("uint8")
        return cv2.LUT(image,table)
        
    
    def clahe(self,image:np.ndarray,clip_limit=1.5,title_grid_size=(8,8))->np.ndarray:
        lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
        l,a,b=cv2.split(lab)
        clahe=cv2.createCLAHE(clipLimit=clip_limit,tileGridSize=title_grid_size)
        l=clahe.apply(l)
        lab=cv2.merge([l,a,b])
        return cv2.cvtColor(lab,cv2.COLOR_LAB2BGR) 
        
    
    def denoise(self,image:np.ndarray,noise_level:float)->np.ndarray:
        if noise_level<200:
            return image
       
        elif noise_level<500:
            return cv2.fastNlMeansDenoisingColored(image,None,5,5,7,21)
        
        else:
            return cv2.fastNlMeansDenoisingColored(image,None,10,10,7,21)
        
    
    def white_balance(self,image:np.ndarray)->np.ndarray:
        b,g,r=cv2.split(image)
        avg_b=np.mean(b)
        avg_g=np.mean(g)
        avg_r=np.mean(r)
        
        gray=(np.mean([avg_b,avg_g,avg_r]))
        eps=1e-6
        kb=gray/(avg_b+eps)
        kg=gray/(avg_g+eps)
        kr=gray/(avg_r+eps)
        
        b=np.clip(b*kb,0,255).astype(np.uint8)
        g=np.clip(g*kg,0,255).astype(np.uint8)
        r=np.clip(r*kr,0,255).astype(np.uint8)
        
        return cv2.merge([b,g,r])
        
    
    def preprocess(self):
       image=self.resize(self.image)
       
       stats=ImageAnalyzer(image).analyze()
       if stats['contrast']>25:
              image=self.white_balance(image)
       stats=ImageAnalyzer(image).analyze()       
       brightness=stats['brightness']
       brightness=max(brightness,1e-6)
       if brightness<60:
           image=self.gamma_correction(image,gamma=1.4)
       elif brightness<90:
              image=self.gamma_correction(image,gamma=1.2)
               
       
        
       new_stats=ImageAnalyzer(image).analyze() 
       
       if new_stats['contrast']<45:
           image=self.clahe(image,clip_limit=1.5,title_grid_size=(8,8))
           
       new_stats=ImageAnalyzer(image).analyze()
       
       image=self.denoise(image,new_stats['noise'])
       
       image = cv2.bilateralFilter(
    image,
    d=7,
    sigmaColor=25,
    sigmaSpace=25
)     
       self.stats = ImageAnalyzer(image).analyze()
       return (image,self.stats)
       