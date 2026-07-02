import cv2
import numpy as np

class EdgeDetector:
    def __init__ (self,image,stats):
        self.image=image
        self.stats=stats
        self.gray=cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
        
    def adaptive_threshold(self,block_size=11,c=10):
        mb=cv2.medianBlur(self.gray,5)
        
        edges=cv2.adaptiveThreshold(mb,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,block_size,c)
        return edges
    

    
    def get_min_component_area(self):

     h, w = self.gray.shape
     area = h * w

     if area < 300000:
        return 60

     elif area < 1000000:
        return 100

     else:
        return 150
    
    def refine_edges(self,edges):
        kernel=np.ones((2,2),np.uint8)
        edges=cv2.morphologyEx(edges,cv2.MORPH_OPEN,kernel)
        edges=cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel)
        edges=self.remove_small_components(edges,self.get_min_component_area())    
        edges=cv2.medianBlur(edges,3)
        return edges
    
    def detect_edges(self):
      return self.portrait_edges()
        
    def remove_small_components(self, edges, min_area=20):
       num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        edges,
        connectivity=8
    )

       cleaned = np.zeros_like(edges) 

       for i in range(1, num_labels):

         area = stats[i, cv2.CC_STAT_AREA]

         if area >= min_area:
            cleaned[labels == i] = 255

       return cleaned    
        
    def portrait_edges(self):

     edges = self.adaptive_threshold()
    

     edges = self.refine_edges(
        edges,)
     edges=cv2.medianBlur(edges,3)

     return cv2.bitwise_not(edges)
            
        
        
        
    