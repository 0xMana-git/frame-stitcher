


#samples per second
sample_rate = 0.5
sample_width = 1000
sample_height = 200
centered_sampling = True
scan_steps = 1
scan_pixels = 1080 - sample_height + 100
#scan_pixels = 500
diff_threshold = sample_width * sample_height * 1
allocated_pixels = 1080 * 150
out_path = "output"
vid_path = "videos_dir"
intermediate_path = "frames"
is_black_and_white = True
pool_size = 32
#doubles processing power but solves some dumb edgecases(sometimes)
enable_rev_check = False