import cfg
from PIL import Image
import numpy as np
import globalvars
from functools import partial

def get_samples_diff(sample0 : np.ndarray, sample1 : np.ndarray):
    #sample0 = sample0.astype("float32")
    sample1 = sample1.astype("float32")
    return np.power(sample0 - sample1, 4).sum() / sample0.size


#sorry i know its a bit messy here
def get_diff_pool_subproc(sample0, img1_array, x_lowbound, x_upbound, current_offset) -> tuple:
    
    if cfg.is_black_and_white:
        sample1 = img1_array[x_lowbound:x_upbound, current_offset:current_offset + cfg.sample_height, 0]
    else:
        sample1 = img1_array[x_lowbound:x_upbound, current_offset:current_offset + cfg.sample_height]
    return (current_offset, get_samples_diff(sample0, sample1))


def get_diff_concurrent(sample0, img1_array, x_lowbound, x_upbound, range_iterator) -> tuple:
    sample0 = sample0.astype("float32")
    get_diff_partial = partial(get_diff_pool_subproc, sample0, img1_array, x_lowbound, x_upbound)
    return min(globalvars.proc_pool.map(get_diff_partial, range_iterator), key=lambda t: t[1])

#img1 should be below img0
def get_stitching_offset(main_image : np.ndarray , additional_image : np.ndarray, main_image_offset : int) -> tuple:

    img_width = additional_image.shape[0]
    #img_height = additional_image.shape[1]

    if not cfg.centered_sampling:
        raise Exception("too lazy to implement this sorry")
    

    #grab sample0, this should be fixed
    x_lowbound = img_width // 2 - cfg.sample_width // 2
    x_upbound = img_width // 2 + cfg.sample_width // 2

    #exclusive to img0 since img1 is variable in the vertical directionsample1 = img1_array[x_lowbound:x_upbound, i:i+cfg.sample_height]
    

    s1_y_lowbound = 0
    s1_y_upbound = cfg.sample_height
    sample1 = additional_image[x_lowbound:x_upbound, s1_y_lowbound:s1_y_upbound]
    #main_image_offset: y location of the "edge"
    start_y = max(main_image_offset - cfg.scan_pixels - cfg.sample_height, 0)
    end_y = main_image_offset - cfg.sample_height

    if cfg.is_black_and_white:
        sample1 = sample1[:, :, 0]


    diff_tuple = get_diff_concurrent(sample1, main_image, x_lowbound, x_upbound, range(start_y, end_y, cfg.scan_steps))
    diff = diff_tuple[1]
    offset = diff_tuple[0]
    #print(f"diff is {diff}")
    return (offset, diff)


    