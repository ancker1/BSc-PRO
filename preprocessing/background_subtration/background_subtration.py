#!/mnt/sdb1/Anaconda/envs/BScPRO/bin/python

"""
Module for background subtration
"""

import glob
import random
from pathlib import Path
import cv2
import numpy as np
#from matplotlib import pyplot as plt

def random_color():
    """ Generate random color """
    rgbl = [255, 0, 0]
    random.shuffle(rgbl)

    return tuple(rgbl)

def show_img(img, window_name, width=640, height=480, wait_key=False):
    """ Show image in certain size """

    resized = cv2.resize(img,
                         (width, height),
                         interpolation=cv2.INTER_NEAREST)

    cv2.imshow(window_name, resized)

    if wait_key is True:
        cv2.waitKey(0)

    return 0

def remove_background(img):
    """ returns image with no background, only table """

    # Find background pixels coordinates
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 0, 64), (179, 51, 255))
    result = cv2.bitwise_and(img, img, mask=mask)

    return mask, result

def run_avg(background_images):
    """
    returns running average of all images in path folder
    """

    avg = np.float32(background_images[0])

    for img in background_images:
        cv2.accumulateWeighted(img, avg, 0.1)

    result = cv2.convertScaleAbs(avg)

    return result

def background_sub(img, background, background_mask):
    """
    returns cropped image(448 x 448) of region of interest
    @img, the image of interest
    """

    # Remove unessesary background
    _img = img.copy()

    # Calculate image difference and find largest contour
    diff = cv2.absdiff(background, _img)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    diff_gray = cv2.bitwise_and(diff_gray, diff_gray, mask=background_mask)
    show_img(diff_gray, 'Difference')

    # Remove small differences
    _, thresh = cv2.threshold(diff_gray, 25, 255, 0)

    # Remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 4))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Get contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cnt_pixel_value = []
    for contour in contours:
        pixel_sum = 0
        x = np.asarray(contour)
        x = x.reshape(x.shape[0], x.shape[2])
        pixel_sum = diff_gray[x[:, :][:, 1], x[:, :][:, 0]]
        cnt_pixel_value.append(np.sum(pixel_sum))

    index = np.argmax(cnt_pixel_value)
    cnt = contours[index]

    # Crop contour form image
    _x, _y, _w, _h = cv2.boundingRect(cnt)
    x_ctr = int((_x + (_x + _w)) / 2)
    y_ctr = int((_y + (_y + _h)) / 2)
    radius = 224
    x_left = x_ctr - radius
    x_right = x_ctr + radius
    y_up = y_ctr - radius
    y_down = y_ctr + radius

    if x_right > img.shape[1]:
        margin = -1 * (img.shape[1] - x_right)
        x_right -= margin
        x_left -= margin
    elif x_left < 0:
        margin = -1 * x_left
        x_right += margin
        x_left += margin

    if y_up < 0:
        margin = -1 * y_up
        y_down += margin
        y_up += margin
    elif y_down > img.shape[0]:
        margin = -1 * (img.shape[0] - y_down)
        y_down -= margin
        y_up -= margin

    img_crop = img[y_up : y_down, x_left : x_right]

    img_rect = img.copy()
    cv2.rectangle(img_rect, (x_left, y_up), (x_right, y_down), random_color(), 4)
    show_img(img_rect, 'Region of interest', wait_key=True)

    return img_crop

def main():
    """ main function """

    ################## IMPORT IMAGES ##################

    # Baggrund
    path = str(Path('images_1280x720/baggrund/bevægelse/*.jpg').resolve())
    background_fil = glob.glob(path)
    background_images = [cv2.imread(img, cv2.IMREAD_COLOR) for img in background_fil]

    # Guleroedder
    path = str(Path('images_1280x720/gulerod/still/*.jpg'))
    carrot_fil = glob.glob(path)
    carrot_images = [cv2.imread(img, cv2.IMREAD_COLOR) for img in carrot_fil]

    # Kartofler
    path = str(Path('images_1280x720/kartofler/still/*.jpg').resolve())
    potato_fil = glob.glob(path)
    potato_images = [cv2.imread(img, cv2.IMREAD_COLOR) for img in potato_fil]

    # Kat laks
    path = str(Path('images_1280x720/kat_laks/still/*.jpg').resolve())
    cat_sal_fil = glob.glob(path)
    cat_sal_images = [cv2.imread(img, cv2.IMREAD_COLOR) for img in cat_sal_fil]

    # Kat okse
    path = str(Path('images_1280x720/kat_okse/still/*.jpg').resolve())
    cat_beef_fil = glob.glob(path)
    cat_beef_images = [cv2.imread(img, cv2.IMREAD_COLOR) for img in cat_beef_fil]

    ################## BACKGROUND SUBTRACTION ##################

    path = str(Path('preprocessing/background_mask.jpg').resolve())
    background_mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    background_img = run_avg(background_images)
    # background_img = cv2.bitwise_and(background_img, background_img, mask=background_mask)

    for img in cat_sal_images:
        roi = background_sub(img, background_img, background_mask)

    cv2.destroyAllWindows()

    return 0

if __name__ == "__main__":
    main()
