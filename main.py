import cv2
import os
import numpy as np 
import dhash
from PIL import Image

def mkdir_if_not_exist(dir : str):
    if not os.path.isdir(dir):
        os.makedirs(dir)



global_redundancy_set = set()
def is_frame_redundant(image) -> bool:
    row, col = dhash.dhash_row_col(image)
    hashed = dhash.format_hex(row, col)
    if hashed in global_redundancy_set:
        return True
    global_redundancy_set.add(hashed)
    return False


vid_path = "./Reading the White Album 2 Manga Online Vol.3 [Part 5] [Oms2iOJfgXY].mkv"
intermediate_path = "frames"
out_path = "output"

def extract_images(path_in, path_out):
    count = 0
    vidcap = cv2.VideoCapture(path_in)
    success, image = vidcap.read()
    success = True
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))    # added this line 
        success,image = vidcap.read()
        image = Image.fromarray(image)
        #print ('Read a new frame: ', success)

        if is_frame_redundant(image):
            print(f"Frame {count} is redundant. Skipping.")
        else:
            image.save(f"{path_out}/{count}.jpg")     # save frame as JPEG file
        count += 1


def main():
    mkdir_if_not_exist(intermediate_path)
    extract_images(vid_path, intermediate_path)


main()