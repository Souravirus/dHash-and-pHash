#!/usr/bin/env python
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
    import os
    def is_image(filename):
        f = filename.lower()
        return f.endswith(".png") or f.endswith(".jpg") or \
            f.endswith(".jpeg") or f.endswith(".bmp") or f.endswith(".gif") or '.jpg' in f
    
    image_filenames = []
    for userpath in userpaths:
        image_filenames += [os.path.join(userpath, path) for path in os.listdir(userpath) if is_image(path)]
    images = {}
    dhash_images = set()
    for img in sorted(image_filenames):
        try:
            hash = dhash(Image.open(img))
        except Exception as e:
            print('Problem:', e, 'with', img)
        if hash in images:
            dhash_images.add(images[hash])
            dhash_images.add(img)
        for i in range(len(hash)):
            hash_list= list(hash)
            if hash_list[i] == '0':
                hash_list[i] = '1'
            else:
                hash_list[i] = '0'
            temp = "".join(hash_list)
            if temp in images:
                dhash_images.add(images[temp])
                dhash_images.add(img)
        #for i in images:
            #print(hamdist(str(images[i]), str(hash)))
            #if(hamdist(images[i], hash) < 2):
                #dhash_images.add(i)
                #dhash_images.add(img)
        images[hash] = img
    #print(images)
    images = {}
    for img in sorted(dhash_images):
        try:
            hash = phash(Image.open(img))
        except Exception as e:
            print('Problem:', e, 'with', img)
        images[hash] = images.get(hash, []) + [img]
    num = 0
    for key in images:
       ele = len(images[key])
       num += (ele*(ele-1))/2
    print(num)
    print(len(image_filenames))
    pic = len(image_filenames)
    den = (pic*(pic-1))/2
    ans = num/den
    print(ans)

if __name__ == '__main__':
    import sys, os
    userpaths = sys.argv[1:] if len(sys.argv) > 1 else "."
    find_similar_images(userpaths=userpaths)
