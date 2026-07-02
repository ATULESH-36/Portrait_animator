from src.pipeline import PortraitPipeline
import cv2
import pathlib
images_folder=pathlib.Path(__file__).parent/"test_images"
image_path=images_folder/'sb11.jpg'
image=cv2.imread(str(image_path))
pipeline=PortraitPipeline()
final_image=pipeline.cartoonify(image)
cv2.imshow('final_output',final_image['final'])
cv2.waitKey(0)
cv2.destroyAllWindows()