import sys, os
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter
if __name__ == '__main__':
    userpath = sys.argv[1]
    count = 1
    for r, d, f in os.walk(userpath):
        for file in f:
            if '.jpg' in file:
                im1 = Image.open(os.path.join(r, file))
                path = os.path.join(userpath+"/../modified_images", "image"+str(count))
                try:
                    os.makedirs(path)
                except OSError as error:
                    print(error)
                im1.save(userpath+"/../modified_images/image"+str(count)+"/im1.jpg")
                enhancer = ImageEnhance.Brightness(im1)
                enhanced_im = enhancer.enhance(1.1)
                enhanced_im.save(userpath+"/../modified_images/image"+str(count)+"/im2.jpg")

                enhancer = ImageEnhance.Contrast(im1)
                enhanced_im = enhancer.enhance(1.1)
                enhanced_im.save(userpath+"/../modified_images/image"+str(count)+"/im3.jpg")

                drawing = ImageDraw.Draw(im1)
                black = (0)
                font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 20) 
                text = "caltech images"
                pos = (10, 10)
                drawing.text(pos, text, fill=black, font=font)
                im1.save(userpath+"/../modified_images/image"+str(count)+"/im4.jpg")

                im1 = Image.open(os.path.join(r, file))
                t_im = im1.convert("L")
                t_im.save(userpath+"/../modified_images/image"+str(count)+"/im5.jpg")

                t_im = im1.resize((64, 64), Image.ANTIALIAS)
                t_im.save(userpath+"/../modified_images/image"+str(count)+"/im6.jpg")

                w, h = im1.size
                t_im = im1.crop((10, 10, w-10, h-10))
                t_im.save(userpath+"/../modified_images/image"+str(count)+"/im7.jpg")

                t_im = im1.filter(ImageFilter.GaussianBlur)
                t_im.save(userpath+"/../modified_images/image"+str(count)+"/im8.jpg")

                im1.save(userpath+"/../modified_images/image"+str(count)+"/im9.jpg", "JPEG", quality = 58)

                im1 = Image.open(os.path.join(r, file))
                enhancer = ImageEnhance.Brightness(im1)
                enhanced_im = enhancer.enhance(0.85)
                enhanced_im.save(userpath+"/../modified_images/image"+str(count)+"/im10.jpg")

                enhancer = ImageEnhance.Contrast(im1)
                enhanced_im = enhancer.enhance(0.85)
                enhanced_im.save(userpath+"/../modified_images/image"+str(count)+"/im11.jpg")
                
                count+=1
