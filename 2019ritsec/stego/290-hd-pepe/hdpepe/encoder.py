import base64
import binascii
import sys
from PIL import Image

def readBin(fname):
    f = open(fname, "rb")
    fstr = base64.b64encode(f.read())
    fdec = fstr.decode('utf-8')
    return fdec

def generateAValues(b64str):
    numArr = []
    for ch in b64str:
        val = ord(ch)
        n = 255 - val
        numArr.append(n)
    return numArr


def readImage(inputImg, encFile, outputImg):
    im = Image.open(inputImg) # Can be many different formats.
    pix = im.load()
    print("[+] Reading image...")
    x_size, y_size = im.size  # Get the width and hight of the image for iterating over
    sizeTup = (x_size, y_size)
    newImg = Image.new('RGBA', sizeTup)
    newPix = newImg.load()
    counter = 0
    print("[+] Reading target file...")
    binStr = readBin(encFile) # read file as bin, return b64 string
    print("[+] Generating new alpha values...")
    aVals = generateAValues(binStr) 
    print("[+] Writing new image...")
    for x in range(x_size):
        for y in range(y_size):
            try:
                r, g, b, a = pix[x, y]
            except:
                r, g, b = pix[x, y]
                a = 255
            if counter >= len(binStr):
                newA = a
            else:
                newA = aVals[counter]
            counter += 1
            newPix[x, y] = (r, g, b, newA)
    print("[+] Saving new image...")
    newImg.save(outputImg)

def main():
    try:
        inpImg = sys.argv[1]
        encFil = sys.argv[2]
        outImg = sys.argv[3]
    except:
        print("USAGE: encoder.py <input_img> <file_to_encode> <output_img>")
        return
    readImage(inpImg, encFil, outImg)

main()