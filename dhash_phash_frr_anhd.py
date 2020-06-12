#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
from PIL import Image, ImageOps
import six
import numpy
import cv2
import matplotlib
import os, sys

def _binary_array_to_hex(arr):
    """
    internal function to make a hex string out of a binary array.
    """
    bit_string = ''.join(str(b) for b in 1 * arr.flatten())
    width = int(numpy.ceil(len(bit_string)/4))
    return '{:0>{width}x}'.format(int(bit_string, 2), width=width)
    
class ImageHash(object):
    """
    Hash encapsulation. Can be used for dictionary keys and comparisons.
    """
    def __init__(self, binary_array):
        self.hash = binary_array
    
    def __str__(self):
        return _binary_array_to_hex(self.hash.flatten())

    def __repr__(self):
        return repr(self.hash)

    def __sub__(self, other):
        if other is None:
            raise TypeError('Other hash must not be None.')
        if self.hash.size != other.hash.size:
            raise TypeError('ImageHashes must be of the same shape.', self.hash.shape, other.hash.shape)
        return numpy.count_nonzero(self.hash.flatten() != other.hash.flatten())

    def __eq__(self, other):
        if other is None:
            return False
        return numpy.array_equal(self.hash.flatten(), other.hash.flatten())

    def __ne__(self, other):
        if other is None:
            return False
        return not numpy.array_equal(self.hash.flatten(), other.hash.flatten())

    def __hash__(self):
        # this returns a 8 bit integer, intentionally shortening the information
        return sum([2**(i % 8) for i, v in enumerate(self.hash.flatten()) if v])

def average_hash(image, hash_size=8):
	"""
	Average Hash computation

	Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

	Step by step explanation: https://www.safaribooksonline.com/blog/2013/11/26/image-hashing-with-python/

	@image must be a PIL instance.
	"""
	if hash_size < 2:
		raise ValueError("Hash size must be greater than or equal to 2")

	# reduce size and complexity, then covert to grayscale
	image = image.convert("L").resize((hash_size, hash_size), Image.ANTIALIAS)

	# find average pixel value; 'pixels' is an array of the pixel values, ranging from 0 (black) to 255 (white)
	pixels = numpy.asarray(image)
	avg = pixels.mean()

	# create string of bits
	diff = pixels > avg
	# make a hash
	return ImageHash(diff)

def whash(image, hash_size = 8, image_scale = None, mode = 'haar', remove_max_haar_ll = True):
	"""
	Wavelet Hash computation.
	
	based on https://www.kaggle.com/c/avito-duplicate-ads-detection/

	@image must be a PIL instance.
	@hash_size must be a power of 2 and less than @image_scale.
	@image_scale must be power of 2 and less than image size. By default is equal to max
		power of 2 for an input image.
	@mode (see modes in pywt library):
		'haar' - Haar wavelets, by default
		'db4' - Daubechies wavelets
	@remove_max_haar_ll - remove the lowest low level (LL) frequency using Haar wavelet.
	"""
	import pywt
	if image_scale is not None:
		assert image_scale & (image_scale - 1) == 0, "image_scale is not power of 2"
	else:
		image_natural_scale = 2**int(numpy.log2(min(image.size)))
		image_scale = max(image_natural_scale, hash_size)

	ll_max_level = int(numpy.log2(image_scale))

	level = int(numpy.log2(hash_size))
	assert hash_size & (hash_size-1) == 0, "hash_size is not power of 2"
	assert level <= ll_max_level, "hash_size in a wrong range"
	dwt_level = ll_max_level - level

	image = image.convert("L").resize((image_scale, image_scale), Image.ANTIALIAS)
	pixels = numpy.asarray(image) / 255

	# Remove low level frequency LL(max_ll) if @remove_max_haar_ll using haar filter
	if remove_max_haar_ll:
		coeffs = pywt.wavedec2(pixels, 'haar', level = ll_max_level)
		coeffs = list(coeffs)
		coeffs[0] *= 0
		pixels = pywt.waverec2(coeffs, 'haar')

	# Use LL(K) as freq, where K is log2(@hash_size)
	coeffs = pywt.wavedec2(pixels, mode, level = dwt_level)
	dwt_low = coeffs[0]

	# Substract median and compute hash
	med = numpy.median(dwt_low)
	diff = dwt_low > med
	return ImageHash(diff)

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

def dhash(image, hash_size = 8):
    image = image.convert("L").resize((hash_size, hash_size + 1), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    # compute differences between columns
    diff = pixels[:, 1:] > pixels[:, :-1]
    bit_string = ''
    for b in 1 * diff.flatten():
        bit_string += str(b)
    print(bit_string)
    return bit_string

def hamdist(str1, str2):
    diffs = 0
    for ch1, ch2 in zip(str1, str2):
        if ch1 != ch2:
            diffs += 1
    return diffs

def find_similar_images(userpath, hashfunc):
    different = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_nham = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for r, d, f in os.walk(userpath):
        for directory in d:
            #print(directory + ":")
            count = 0
            parent_hash = ""
            curr_dir = os.path.join(userpath + directory)
            image_filenames = []
            image_filenames += [os.path.join(curr_dir, path) for path in os.listdir(curr_dir)]
            for img in sorted(image_filenames):
                #print(img + ":")
                if count == 0:
                    parent_hash += str(hashfunc(Image.open(img)))
                else:
                    curr_hash = str(hashfunc(Image.open(img)))
                    #ham = hamdist(parent_hash, curr_hash)
                    #nham = ham/64
                    #total_nham[count-1] += nham
                    if curr_hash != parent_hash:
                        different[count-1] += 1
                count += 1
    #avg_nham = [x / 9103 for x in total_nham]
    #print(avg_nham)
    print(different)

if __name__ == '__main__':
    import sys, os
    def usage():
        sys.stderr.write("""SYNOPSIS: %s [ahash|phash|dhash|...] [<directory>]

Identifies similar images in the directory.
Method: 
  ahash:      Average hash
  phash:      Perceptual hash
  dhash:      Difference hash
  whash: Haar wavelet hash
  whash-db4:  Daubechies wavelet hash
  """ % sys.argv[0])
        sys.exit(1)
    
    hashmethod = sys.argv[1] if len(sys.argv) > 1 else usage()
    if hashmethod == 'ahash':
        hashfunc = average_hash
    elif hashmethod == 'phash':
        hashfunc = phash
    elif hashmethod == 'dhash':
        hashfunc = dhash
    elif hashmethod == 'whash':
        hashfunc = whash
    else:
        usage()
    userpath = sys.argv[2]
    find_similar_images(userpath=userpath, hashfunc=hashfunc)
