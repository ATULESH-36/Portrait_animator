import cv2
import pathlib
from src.pipeline import PortraitPipeline

def save_demo_images(results):
    assets=pathlib.Path(__file__).parent / "assets"
    
    cv2.imwrite(str(assets/'Original.jpg'),results['original'])
    
    cv2.imwrite(str(assets/'preprocessed.jpg'),results['preprocessed'])
    
    cv2.imwrite(str(assets/'quantized.jpg'),results['quantized'])
    
    cv2.imwrite(str(assets/'edges.jpg'),results['edges'])
    
    cv2.imwrite(str(assets/'cartoon.jpg'),results['cartoon'])
    
    cv2.imwrite(str(assets/'final.jpg'),results['final'])

image_folder=pathlib.Path(__file__).parent/'test_images'
image_name=input("enter the image path :")
image_path=image_folder/image_name
image=cv2.imread(str(image_path))
pipeline = PortraitPipeline()
results = pipeline.cartoonify(image)

if results is None:
    print("Cartoonification failed.")
    exit()

save_demo_images(results)

cv2.imshow("Final Cartoon", results["final"])
cv2.waitKey(0)
cv2.destroyAllWindows()

    
    