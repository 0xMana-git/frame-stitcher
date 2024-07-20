import cv2
import os
import numpy as np 
import dhash
from PIL import Image
import re
import stitcher
import cfg
import shutil
import subprocess
from multiprocessing import Manager, Pool
from functools import partial
import globalvars
def mkdir_if_not_exist(dir : str):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)


def is_frame_redundant(shared_dict, image) -> bool:
    row, col = dhash.dhash_row_col(image)
    hashed = dhash.format_hex(row, col)
    if hashed in shared_dict.keys():
        return True
    shared_dict[hashed] = True
    return False

def is_redundant_subproc(shared_dict, fname) -> bool:
    with Image.open(fname) as image:
        return (fname, is_frame_redundant(shared_dict, image))


def strip_redundant(frames_dir):
    manager = Manager()
    shared_dict = manager.dict()
    redundant_partial = partial(is_redundant_subproc, shared_dict)

    frames = sorted_alphanumeric(os.listdir(frames_dir))
    for i in range(len(frames)):
        frames[i] = f"{frames_dir}/{frames[i]}"

    redundant_files = globalvars.proc_pool.map(redundant_partial, frames)
    for entry_tuple in redundant_files:
        if entry_tuple[1]:
            print(f"Removing redundant frame {entry_tuple[0]}")
            os.remove(entry_tuple[0])
    
def rename_non_redundant(frames_dir):
    frames = sorted_alphanumeric(os.listdir(frames_dir))
    for i in range(len(frames)):
        frames[i] = f"{frames_dir}/{frames[i]}"
        frame_new = f"{frames_dir}/{i}.png"
        os.rename(frames[i], frame_new)

def extract_images(path_in, path_out):
    mkdir_if_not_exist(path_out)
    subprocess.run(["ffmpeg", "-hwaccel", "auto", "-i", path_in, "-r", str( 1 / cfg.sample_rate), f"{path_out}/%d.png"])
    strip_redundant(path_out)
    

        
    
def stitch_all(path_in, path_out):
    img_filenames = sorted_alphanumeric(os.listdir(path_in))
    first_image = Image.open(f"{path_in}/{img_filenames[0]}")
    cur_offset = first_image.size[1]

    final_image = Image.new(first_image.mode, (first_image.size[0], cfg.allocated_pixels))
    final_image.paste(first_image)
    #final_image.save(f"{path_out}/out.png")
    for i in range(len(img_filenames) - 1):
        img_name = f"{path_in}/{img_filenames[i + 1]}"
        print(f"Processing {i + 1} of {len(img_filenames)} images({img_name})")
        second_image = Image.open(img_name)
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
    globalvars.proc_pool = Pool(cfg.pool_size)
    for vid in os.listdir(cfg.vid_path):
        cur_vid = f"{cfg.vid_path}/{vid}"
        cur_out = f"{cfg.out_path}/{vid.rsplit(".", 1)[0]}"
        print(f"\n\n\nProcessing video {cur_vid}...\n")

        #shutil.rmtree(cfg.intermediate_path)
        #extract_images(cur_vid, cfg.intermediate_path)
        rename_non_redundant(cfg.intermediate_path)
        stitch_all(cfg.intermediate_path, cur_out)

if __name__ == "__main__":
    main()
