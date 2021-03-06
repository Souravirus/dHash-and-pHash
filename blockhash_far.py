#! /usr/bin/env python
#
# Perceptual image hash calculation tool based on algorithm descibed in
# Block Mean Value Based Image Perceptual Hashing by Bian Yang, Fan Gu and Xiamu Niu
#
# Copyright 2014 Commons Machinery http://commonsmachinery.se/
# Distributed under an MIT license, please see LICENSE in the top dir.

import math
import argparse
import PIL.Image as Image

def median(data):
    data = sorted(data)
    length = len(data)
    if length % 2 == 0:
        return (data[length // 2 - 1] + data[length // 2]) / 2.0
    return data[length // 2]

def total_value_rgba(im, data, x, y):
    r, g, b, a = data[y * im.size[0] + x]
    if a == 0:
        return 765
    else:
        return r + g + b

def total_value_rgb(im, data, x, y):
    r, g, b = data[y * im.size[0] + x]
    return r + g + b

def translate_blocks_to_bits(blocks, pixels_per_block):
    half_block_value = pixels_per_block * 256 * 3 / 2

    # Compare medians across four horizontal bands
    bandsize = len(blocks) // 4
    for i in range(4):
        m = median(blocks[i * bandsize : (i + 1) * bandsize])
        for j in range(i * bandsize, (i + 1) * bandsize):
            v = blocks[j]

            # Output a 1 if the block is brighter than the median.
            # With images dominated by black or white, the median may
            # end up being 0 or the max value, and thus having a lot
            # of blocks of value equal to the median.  To avoid
            # generating hashes of all zeros or ones, in that case output
            # 0 if the median is in the lower value space, 1 otherwise
            blocks[j] = int(v > m or (abs(v - m) < 1 and m > half_block_value))


def bits_to_hexhash(bits):
    return '{0:0={width}x}'.format(int(''.join([str(x) for x in bits]), 2), width = len(bits) // 4)


def blockhash_even(im, bits):
    if im.mode == 'RGBA':
        total_value = total_value_rgba
    elif im.mode == 'RGB':
        total_value = total_value_rgb
    else:
        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

    data = im.getdata()
    width, height = im.size
    blocksize_x = width // bits
    blocksize_y = height // bits

    result = []

    for y in range(bits):
        for x in range(bits):
            value = 0

            for iy in range(blocksize_y):
                for ix in range(blocksize_x):
                    cx = x * blocksize_x + ix
                    cy = y * blocksize_y + iy
                    value += total_value(im, data, cx, cy)

            result.append(value)

    translate_blocks_to_bits(result, blocksize_x * blocksize_y)
    return bits_to_hexhash(result)

def blockhash(im, bits):
    if im.mode == 'RGBA':
        total_value = total_value_rgba
    elif im.mode == 'RGB':
        total_value = total_value_rgb
    else:
        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

    data = im.getdata()
    width, height = im.size

    even_x = width % bits == 0
    even_y = height % bits == 0

    if even_x and even_y:
        return blockhash_even(im, bits)

    blocks = [[0 for col in range(bits)] for row in range(bits)]

    block_width = float(width) / bits
    block_height = float(height) / bits

    for y in range(height):
        if even_y:
            # don't bother dividing y, if the size evenly divides by bits
            block_top = block_bottom = int(y // block_height)
            weight_top, weight_bottom = 1, 0
        else:
            y_frac, y_int = math.modf((y + 1) % block_height)

            weight_top = (1 - y_frac)
            weight_bottom = (y_frac)

            # y_int will be 0 on bottom/right borders and on block boundaries
            if y_int > 0 or (y + 1) == height:
                block_top = block_bottom = int(y // block_height)
            else:
                block_top = int(y // block_height)
                block_bottom = int(-(-y // block_height)) # int(math.ceil(float(y) / block_height))

        for x in range(width):
            value = total_value(im, data, x, y)

            if even_x:
                # don't bother dividing x, if the size evenly divides by bits
                block_left = block_right = int(x // block_width)
                weight_left, weight_right = 1, 0
            else:
                x_frac, x_int = math.modf((x + 1) % block_width)

                weight_left = (1 - x_frac)
                weight_right = (x_frac)

                # x_int will be 0 on bottom/right borders and on block boundaries
                if x_int > 0 or (x + 1) == width:
                    block_left = block_right = int(x // block_width)
                else:
                    block_left = int(x // block_width)
                    block_right = int(-(-x // block_width)) # int(math.ceil(float(x) / block_width))

            # add weighted pixel value to relevant blocks
            blocks[block_top][block_left] += value * weight_top * weight_left
            blocks[block_top][block_right] += value * weight_top * weight_right
            blocks[block_bottom][block_left] += value * weight_bottom * weight_left
            blocks[block_bottom][block_right] += value * weight_bottom * weight_right

    result = [blocks[row][col] for row in range(bits) for col in range(bits)]

    translate_blocks_to_bits(result, block_width * block_height)
    return bits_to_hexhash(result)
        

def block(image):

    interpolation = Image.ANTIALIAS

    if image.mode == '1' or image.mode == 'L' or image.mode == 'P':
        image = image.convert('RGB')
    elif image.mode == 'LA':
        image = image.convert('RGBA')

    method = blockhash

    size = (256,256)
    image = image.resize(size, interpolation)

    hash = method(image, 8)
    #print(hash)
    bin_hash = format(int(hash, 16), "040b")
    #print(bin_hash)
    return(bin_hash)

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
    far_count = 0
    for img in sorted(image_filenames):
        try:
            hash = block(Image.open(img))
        except Exception as e:
            print('Problem:', e, 'with', img)
        if hash in images:
            far_count+=1
        images[hash] = images.get(hash, []) + [img]
    num = 0
    for key in images:
       ele = len(images[key])
       num += (ele*(ele-1))/2
    #print("far_count:")
    #print(far_count)
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
