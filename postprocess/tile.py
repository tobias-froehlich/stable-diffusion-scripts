import numpy as np
import os
from PIL import Image
import sys
import const

path = const.PATH

def getImage(prefix):
    for filename in os.listdir(path):
        if filename.startswith(prefix) and filename.endswith(".png"):
            return filename
    return None

def calculateCoordinates(height, width, i, j):
    jmin = max(0, j - 1)
    imin = max(0, i - 1)
    jmax = min(width, j + 2)
    imax = min(height, i + 2)
    xmin = jmin * 192
    ymin = imin * 192
    xmax = jmax * 192
    ymax = imax * 192
    xholemin = j * 192
    yholemin = i * 192
    xholemax = (j + 1) * 192
    yholemax = (i + 1) * 192
    return (xmin, xholemin, xholemax, xmax, ymin, yholemin, yholemax, ymax)

def prepareInit(manager):
    height = manager.getHeight()
    width = manager.getWidth()
    i = manager.getI()
    j = manager.getJ()
    promptmask = manager.getPromptmask()["mask"]
    fullFilename = manager.getLastFullFilename()
    (xmin, xholemin, xholemax, xmax, ymin, yholemin, yholemax, ymax) = manager.getCoordinates()
    im = np.array(Image.open(os.path.join(path, fullFilename)))
    print(im.shape)
    alpha = np.expand_dims(np.zeros((im.shape[0], im.shape[1]), dtype=im.dtype), 2) + 255 
    print(alpha.shape)
    print(promptmask)
    alpha[yholemin:yholemax,xholemin:xholemax] = 255 - promptmask[yholemin:yholemax,xholemin:xholemax]
    print(alpha.shape)
    im = im[ymin:ymax,xmin:xmax]
    print(im.shape)
    alpha = alpha[ymin:ymax,xmin:xmax]
    print(alpha.shape)
    if (im.shape[2] == 4):
        im = im[:, :, 0:3]
    print(im.shape)
    im = np.concatenate([im, alpha], 2)
    print(im.shape)
    initFilename = manager.getInitFilename()
    Image.fromarray(im).save(os.path.join(path, initFilename))

fullmask = np.zeros((192*3, 192*3, 1))
for y in range(192*3):
    for x in range(192*3):
        dx = max(0, 192 - x, x - 192*2)
        dy = max(0, 192 - y, y - 192*2)
        d = np.sqrt(min(1.0, (dx / 192)**2 + (dy / 192)**2))
        fullmask[y, x] = 1.0 - d


def getMask(xmin, xholemin, xholemax, xmax, ymin, yholemin, yholemax, ymax):
    xstart = 0
    ystart = 0
    xend = 192*3
    yend = 192*3
    if xmin == xholemin:
        xstart = 192
    if xmax == xholemax:
        xend = 192*2
    if ymin == yholemin:
        ystart = 192
    if ymax == yholemax:
        yend = 192*2
    return fullmask[ystart:yend,xstart:xend]

print(fullmask.mean())


def replaceOutput(manager, prefix):
    height = manager.getHeight()
    width = manager.getWidth()
    i = manager.getI()
    j = manager.getJ()
    lastFullFileName = manager.getLastFullFilename()
    full = np.array(Image.open(os.path.join(path, lastFullFileName)))
    output = np.array(Image.open(os.path.join(path, getImage(prefix))))
    if full.shape[2] == 4:
        full = full[:, :, 0:3]
    if output.shape[2] == 4:
        output = output[:, :, 0:3]
    (xmin, xholemin, xholemax, xmax, ymin, yholemin, yholemax, ymax) = manager.getCoordinates()
    original = full[ymin:ymax,xmin:xmax]
    mask = getMask(xmin, xholemin, xholemax, xmax, ymin, yholemin, yholemax, ymax)
    blended = output * mask + original * (1.0 - mask)
    blended = np.array(blended, dtype=full.dtype)
    full[ymin:ymax,xmin:xmax] = blended
    currentFullFilename = manager.getCurrentFullFilename()
    Image.fromarray(full).save(os.path.join(path, currentFullFilename))
    

