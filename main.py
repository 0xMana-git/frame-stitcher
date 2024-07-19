import cv2
import os
import numpy as np 
import dhash
from PIL import Image
import re
import stitcher
import cfg
import shutil


def mkdir_if_not_exist(dir : str):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

global_redundancy_set = set()
def is_frame_redundant(image) -> bool:
    row, col = dhash.dhash_row_col(image)
    hashed = dhash.format_hex(row, col)
    if hashed in global_redundancy_set:
        return True
    global_redundancy_set.add(hashed)
    return False



def extract_images(path_in, path_out):
    count = 0
    vidcap = cv2.VideoCapture(path_in)
    success, image = vidcap.read()
    success = True
    while success:
        try:
            vidcap.set(cv2.CAP_PROP_POS_MSEC, int(count * 1000 * (1 / cfg.sample_rate)))    
            success,image = vidcap.read()
            image = Image.fromarray(image)
            #print ('Read a new frame: ', success)

            if is_frame_redundant(image):
                print(f"Frame {count} is redundant. Skipping.")
            else:
                image.save(f"{path_out}/{count}.png") 
            count += 1
        except:
            print("Exception Occured. Halting image extraction.")
            return

def stitch_all(path_in, path_out):
    img_filenames = sorted_alphanumeric(os.listdir(path_in))
    first_image = Image.open(f"{path_in}/{0}.png")
    cur_offset = first_image.size[1]

    final_image = Image.new(first_image.mode, (first_image.size[0], cfg.allocated_pixels))
    final_image.paste(first_image)
    #final_image.save(f"{path_out}/out.png")
    for i in range(len(img_filenames) - 1):
        print(f"Processing {i + 1} of {len(img_filenames)} images")
        second_image = Image.open(f"{path_in}/{img_filenames[i + 1]}")
        offset = stitcher.get_stitching_offset(first_image, second_image)
        #update only if passed diff threshold
        #probably redundant now
        if offset == -1:
            print(f"Ignored {i} due to diff being too high")
            continue
        #paste into final image according to offset
        #also i think im kinda fucked if the manga scrolled back idk
        cur_offset -= offset
        final_image.paste(second_image, (0, cur_offset))
        #final_image.save(f"{path_out}/out.png")
        cur_offset += second_image.size[1]
        first_image = second_image
    mkdir_if_not_exist(path_out)
    actual_final_image = Image.new(final_image.mode, (final_image.size[0], cur_offset))
    actual_final_image.paste(final_image)
    actual_final_image.save(f"{path_out}/out.png")
    
        


def main():
    shutil.rmtree(cfg.intermediate_path)
    mkdir_if_not_exist(cfg.intermediate_path)
    extract_images(cfg.vid_path, cfg.intermediate_path)
    stitch_all(cfg.intermediate_path, cfg.out_path)

main()