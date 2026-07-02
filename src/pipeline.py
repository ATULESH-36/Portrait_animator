import cv2
from src.image_analysis import ImageAnalyzer
from src.preprocessing import ImagePreProcessor
from src.edge_detection import EdgeDetector
from src.color_quantization import ColorQuantizer
from src.cartoonizer import PortraitCartoonizer
from src.postprocess import PostProcessor

class PortraitPipeline:
    
    
    def cartoonify(self,image):
        ##Analyze the image
      try:  
        if image is None:
            raise ValueError("Input image is None. Please provide a valid image.")
        
        if len(image.shape) != 3:
         raise ValueError(
        "Input must be a color image."
    )
            
        image_analyzer=ImageAnalyzer(image)
        image_stats=image_analyzer.analyze()
        
        ##Image preprocessing
        image_preprocessor=ImagePreProcessor(image,image_stats)
        preprocessed_image,stats=image_preprocessor.preprocess()
        
        ##color quantization
        quantized_image=ColorQuantizer(preprocessed_image,stats).quantize()
        
        ##edge detection
        edge_detector=EdgeDetector(preprocessed_image,stats)
        
        edges=edge_detector.detect_edges()
        
        ##overlaying 
        merger=PortraitCartoonizer(preprocessed_image,quantized_image,edges,stats)
        cartoon=merger.overlay()
        
        ##post processing
        Post_processor=PostProcessor(cartoon)
        final_image=Post_processor.process()
        return {
    "original": image,
    "preprocessed": preprocessed_image,
    "quantized": quantized_image,
    "edges": edges,
    "cartoon": cartoon,
    "final": final_image
}
      except Exception as e:
        print(f"Error during cartoonification: {e}")
        return None  