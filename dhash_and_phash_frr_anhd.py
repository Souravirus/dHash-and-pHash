from __future__ import (absolute_import, division, print_function)
from PIL import Image, ImageOps
import six
import numpy

def phash(image, hash_size=8, highfreq_factor=4):
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    import scipy.fftpack
    img_size = hash_size * highfreq_factor
    image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = numpy.median(dctlowfreq)
    diff = dctlowfreq > med
    bit_string = ''
    for b in 1 * diff.flatten():
        bit_string += str(b)
    return bit_string

def dhash(image, hash_size = 7):
    image = image.convert("L").resize((hash_size, hash_size + 1), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    # compute differences between columns
    diff = pixels[:, 1:] > pixels[:, :-1]
    bit_string = ''
    for b in 1 * diff.flatten():
        bit_string += str(b)
    #print(bit_string)
    return bit_string

def hamdist(str1, str2):
    diffs = 0
    for ch1, ch2 in zip(str1, str2):
        if ch1 != ch2:
            diffs += 1
    return diffs

def find_similar_images(userpaths):
    different = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_nham = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for r, d, f in os.walk(userpaths):
        for directory in d:
            #print(directory + ":")
            count = 0
            parent_dhash = ""
            parent_phash = ""
            curr_dir = os.path.join(userpaths + directory)
            image_filenames = []
            image_filenames += [os.path.join(curr_dir, path) for path in os.listdir(curr_dir)]
            for img in sorted(image_filenames):
                if count == 0:
                    parent_dhash += dhash(Image.open(img))
                    parent_phash += phash(Image.open(img))

                else:
                    curr_dhash = dhash(Image.open(img))
                    if hamdist(curr_dhash, parent_dhash) > 1:
                        different[count-1] += 1
                        #ham = hamdist(parent_dhash, curr_dhash)
                        #nham = ham/49
                        #total_nham[count-1] += nham
                    else:
                        curr_phash = phash(Image.open(img))
                        #ham = hamdist(parent_phash, curr_phash)
                        #nham = ham/64
                        #total_nham[count-1] += nham
                        if curr_phash != parent_phash:
                            different[count-1] += 1
                count += 1
    #avg_nham = [x / 9103 for x in total_nham]
    #print(avg_nham)
    print(different)

if __name__ == '__main__':
    import sys, os
    userpaths = sys.argv[1]
    find_similar_images(userpaths=userpaths)
