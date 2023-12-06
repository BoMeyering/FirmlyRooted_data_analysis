# Utility functions to manipulate video footage

import os
import imageio
import pims


def movie_splitter(filename, target_dir) -> tuple[int, int]:
    """
    Take a movie file supported by PIMS.ImageIOReader
    Split into individual frames
    Saves greyscale images in target directory
    Returns a tuple with the number of images and the framerate of the video
    :param filename: an absolute or relative filepath
    :param target_dir: a path to a directory that may or may not exist
    :return: tuple[rate, vlen]
    """

    assert os.path.exists(filename), "Error: This file does not exist"

    try:
        assert os.path.exists(target_dir)
    except AssertionError:
        print(f"Making directory {target_dir} for image output")
        os.mkdir(target_dir)

    vid = pims.ImageIOReader(filename)
    rate = vid.frame_rate
    vlen = len(vid) - 1

    target_dir += "/"

    for f in range(vlen):
        frame = vid[f][:, :, 0]
        imageio.imwrite(f"{target_dir}{f}.jpeg", frame)

    print(f"Video {filename} frames captured")

    return vlen, rate
