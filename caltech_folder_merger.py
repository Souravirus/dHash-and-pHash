import sys, os
from PIL import Image
if __name__ == '__main__':
    userpath = sys.argv[1]
    count = 1
    for r, d, f in os.walk(userpath):
        for file in f:
            if ".jpg" in file:
                print(file)
                im1 = Image.open(os.path.join(r, file))
                im1.save("image" + str(count) + ".jpg")
                count+=1

