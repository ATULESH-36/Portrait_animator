import cv2
import numpy as np
from src.image_analysis import ImageAnalyzer
from src.edge_detection import EdgeDetector
from src.color_quantization import ColorQuantizer

class PortraitCartoonizer:
    def __init__(self,image,quantized,edges,stats):
        self.image=image
        self.quantized=quantized
        self.edges=edges
        self.stats=stats
        
    def portrait_overlay(self,edge_color=(25,10,15),alpha=0.8):
        cartoon=self.quantized.copy()
        edge_pixels=self.edges>0
        edge_color=np.array(edge_color,dtype=np.uint8)
        cartoon=cartoon.astype(np.float32)
        cartoon[edge_pixels]=(alpha*edge_color+(1-alpha)*cartoon[edge_pixels])
        return np.clip(cartoon,0,255).astype(np.uint8)
        
    def soft_cartoon(self):
     return cv2.addWeighted(
        self.quantized,
        0.6,
        self.portrait_overlay(),
        0.4,
        0
    )    
    
    def auto_select(self):
     edge_density = self.stats["edge_density"]
     contrast = self.stats["contrast"]

     if edge_density < 0.05 and contrast < 50:
        return self.quantized

     elif edge_density < 0.10:
        return self.soft_cartoon()

     else:
        return self.portrait_overlay() 
        
    
    def overlay(self, style='auto'):
     style = style.lower()

     if style == 'quantized':
        return self.quantized

     elif style == 'cartoon':
        return self.portrait_overlay()

     elif style == 'soft':
        return self.soft_cartoon()

     elif style == 'auto':
        return self.auto_select()

     else:
        raise ValueError("Invalid style.")
        
    