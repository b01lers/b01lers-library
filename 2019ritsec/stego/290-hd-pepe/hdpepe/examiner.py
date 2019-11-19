from PIL import Image
import sys

def examine(fname, maxpix):
    im = Image.open(fname) # Can be many different formats.
    pix = im.load()
    x_size, y_size = im.size  # Get the width and hight of the image for iterating over
    print("X-axis size: " + str(x_size))
    print("Y-axis size: " + str(y_size))
    counter = 0
    for x in range(x_size):
        for y in range(y_size):
            if str(counter) == maxpix:
                return
            try:
                r, g, b, a = pix[x, y]
            except:
                r, g, b = pix[x, y]
                a = 255
            print("r: {}, g: {}, b: {}, a: {}".format(r, g, b, a))
            counter += 1

def main():
    try:
        fname = sys.argv[1]
        maxpix = sys.argv[2]
    except:
        print("USAGE: examiner.py <image_name> <pixels_to_examine>")
        exit()
    examine(fname, maxpix)
    return

main()