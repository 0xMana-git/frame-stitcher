import cfg
from PIL import Image
import numpy as np
import globalvars
from functools import partial

def get_samples_diff(sample0 : np.ndarray, sample1 : np.ndarray):
    sample0 = sample0.astype("float32")
    sample1 = sample1.astype("float32")
    return np.power(sample0 - sample1, 4).sum() / sample0.size


#sorry i know its a bit messy here
def get_diff_pool_subproc(sample0, img1_array, x_lowbound, x_upbound, current_offset) -> tuple:
    sample1 = img1_array[x_lowbound:x_upbound, current_offset:current_offset + cfg.sample_height]
    return (current_offset, get_samples_diff(sample0, sample1))


def get_diff_concurrent(sample0, img1_array, x_lowbound, x_upbound, range_iterator) -> tuple:
    get_diff_partial = partial(get_diff_pool_subproc, sample0, img1_array, x_lowbound, x_upbound)
    return min(globalvars.proc_pool.map(get_diff_partial, range_iterator), key=lambda t: t[1])

#img1 should be below img0
def get_stitching_offset(img0 , img1) -> int:
    img0_array : np.ndarray = np.array(img0).swapaxes(0, 1)
    img1_array : np.ndarray = np.array(img1).swapaxes(0, 1)
    if cfg.is_black_and_white:
        img0_array = img0_array[:, :, 0]
        img1_array = img1_array[:, :, 0]

    #assume both have the same dims, which they should
    img_width = img0_array.shape[0]
    img_height = img0_array.shape[1]

    if not cfg.centered_sampling:
        raise Exception("too lazy to implement this sorry")
    

    #grab sample0, this should be fixed
    x_lowbound = img_width // 2 - cfg.sample_width // 2
    x_upbound = img_width // 2 + cfg.sample_width // 2

    #exclusive to img0 since img1 is variable in the vertical directionsample1 = img1_array[x_lowbound:x_upbound, i:i+cfg.sample_height]
    

    s0_y_lowbound = img_height - cfg.sample_height
    s0_y_upbound = img_height
    sample0 = img0_array[x_lowbound:x_upbound, s0_y_lowbound:s0_y_upbound]


    diff_tuple = get_diff_concurrent(sample0, img1_array, x_lowbound, x_upbound, range(0, cfg.scan_pixels, cfg.scan_steps))
    diff = diff_tuple[1]
    offset = diff_tuple[0]

    if diff > cfg.diff_threshold:
        return -1
    return offset + cfg.sample_height


    