from PIL import Image
import pathlib

assets = pathlib.Path("assets")

frames = []

files = [
    "original.jpg",
    "preprocessed.jpg",
    "quantized.jpg",
    "edges.jpg",
    "final.jpg"
]

for file in files:
    frames.append(Image.open(assets / file))

frames[0].save(
    assets / "demo.gif",
    save_all=True,
    append_images=frames[1:],
    duration=1200,
    loop=0
)

print("demo.gif created.")