import os
from PIL import Image
import PIL
import glob

input_path = 'comp/'
output_path = 'comp_out/'


def compress_image():
    print("Start compressing images")
    for entry in os.scandir(input_path):
        if entry.is_dir():
            for e in os.scandir(entry):
                print(e.path)
                img = Image.open(e.path)
                b_size = os.path.getsize(e.path)
                w, h = img.size
                rt = img.resize((int(w*0.5), int(h*0.5)), Image.ANTIALIAS)
                # print(f"The image size dimensions are: {img.size}")
                print("size before compress:" + str(b_size))
                if e.name.endswith('.png'):
                    rgb_img = rt.convert('RGB')
                    ext = os.path.splitext(e.name)[0] + '.jpg'
                    p = entry.path + "/" + ext
                    rgb_img.save(p, optimize=True, quality=20)
                    a_size = os.path.getsize(p)
                    os.remove(e.path)
                    print("size after compress:" + str(a_size))
                else:
                    os.remove(e.path)
                    ext = os.path.splitext(e.name)[0] + '.jpg'
                    p = entry.path + "/" + ext
                    rt.save(p, optimize=True, quality=20)
                    a_size = os.path.getsize(e.path)
                    print("size after compress:" + str(a_size))

    print("Done compress")


if __name__ == "__main__":
    compress_image()
