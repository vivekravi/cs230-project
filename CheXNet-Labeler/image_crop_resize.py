import cv2
import numpy as np
import os


image_path = 'MIMIC_images_crop_1201/'
output_path = 'MIMIC_images_norm_1201/'


def crop_resize_img(img):
    img_height = img.shape[0]
    img_width = img.shape[1]
    # Find the left and right borders
    ref_pixel_loc = [0, -1]
    lr_border_count = [0, 0]
    for idx, l in enumerate(ref_pixel_loc):
        ref_pixel = img[0, l]
        sign_pixel = np.sign(l)
        if sign_pixel == 0:
            sign_pixel = 1
        sum_pixel = 0
        while sum_pixel == 0:
            sum_pixel = np.sum(np.abs(img[:, l] - ref_pixel))
            if sum_pixel == 0:
                lr_border_count[idx] += 1
            l += sign_pixel
    if lr_border_count[1] >= img_width - lr_border_count[0]:
        lr_border_count[1] = img_width - lr_border_count[0] - 1
    # Find top borders
    ref_pixel = img[0, 0]
    sum_pixel = 0
    l = 0
    t_border_count = 0
    while sum_pixel == 0:
        sum_pixel = np.sum(np.abs(img[l, :] - ref_pixel))
        if sum_pixel == 0:
            t_border_count += 1
        l += 1    
    b_border_count = img_height - (img_width - (lr_border_count[1] + lr_border_count[0])) - t_border_count
    if b_border_count < 0:
        b_border_count = 0
    if b_border_count >= img_height - t_border_count:
        b_border_count = img_height - t_border_count - 1
    
    print(lr_border_count)
    print([t_border_count, b_border_count])
    img_crop = img[t_border_count: img_height - b_border_count, lr_border_count[0]: img_width - lr_border_count[1]]
    img_resize = cv2.resize(img_crop, (1024, 1024))
    return img_resize


def img_normalize(img):
    img_height = img.shape[0]
    start_h = int(img_height * 0.3)
    img = img / float(img[start_h:, :, :].max()) * 255
    return np.uint8(img)


if __name__ == "__main__":
    c = 0
    for img_name in sorted(os.listdir(image_path)):
        if img_name.endswith('png'):
            print(os.path.join(image_path, img_name))
            print(c)
            img = cv2.imread(os.path.join(image_path, img_name))
            if img is not None:
#                 img_crop_resize = crop_resize_img(img)
#                 cv2.imwrite(os.path.join(output_path, img_name), img_crop_resize)
                img_norm = img_normalize(img)
                cv2.imwrite(os.path.join(output_path, img_name), img_norm)
        c += 1
        