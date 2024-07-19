import cfg
from PIL import Image
import numpy as np
def get_samples_diff(sample0 : np.ndarray, sample1 : np.ndarray):
    return np.absolute(sample0 - sample1).sum()

#img1 should be below img0
def get_stitching_offset(img0 , img1) -> int:
    img0_array : np.ndarray = np.array(img0).swapaxes(0, 1)
    img1_array : np.ndarray = np.array(img1).swapaxes(0, 1)

    #assume both have the same dims, which they should
    img_width = img0_array.shape[0]
    img_height = img0_array.shape[1]

    if not cfg.centered_sampling:
        raise Exception("too lazy to implement this sorry")
    

    #grab sample0, this should be fixed
    x_lowbound = img_width // 2 - cfg.sample_width // 2
    x_upbound = img_width // 2 + cfg.sample_width // 2

    #exclusive to img0 since img1 is variable in the vertical direction
    s0_y_lowbound = img_height - cfg.sample_height
    s0_y_upbound = img_height
    sample0 = img0_array[x_lowbound:x_upbound, s0_y_lowbound:s0_y_upbound]

    maxdiff = cfg.diff_threshold 
    offset = 0

    for i in range(0, cfg.scan_pixels, cfg.scan_steps):
        sample1 = img1_array[x_lowbound:x_upbound, i:i+cfg.sample_height]
        diff = get_samples_diff(sample0, sample1)
        if diff < maxdiff:
            maxdiff = diff
            offset = i
            print(diff)
    if maxdiff == cfg.diff_threshold:
        return -1
    return offset + cfg.sample_height


    