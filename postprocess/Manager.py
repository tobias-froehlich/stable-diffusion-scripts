import numpy as np
import os
from PIL import Image

class Manager:
    def __init__(self, directory, height, width):
        self.__directory = directory
        self.__width = width
        self.__height = height
        self.__readPromptmasks()
        self.__tileIndex = 0
        self.__checkImageSizes()

    def __readPromptmasks(self):
        promptmasks = []
        for filename in os.listdir(self.__directory):
            if filename.startswith("mask_") and filename.endswith(".png"):
                im = np.array(Image.open(os.path.join(self.__directory, filename)))
                im = im[:, :, 0:1]
                words = filename.split(".")[0].split("_")
                print(words)
                promptmasks.append({
                    "index": int(words[1]),
                    "prompt": " ".join(words[2:]),
                    "mask": im,
                })
        self.__promptmasks = sorted(promptmasks, key=lambda x : x["index"])
        for i in range(len(promptmasks)):
            assert self.__promptmasks[i]["index"] == i + 1, "The promptmasks must be numerated starting with 1."
        
        self.__activeTiles = []
        for promptmask in self.__promptmasks:
            for i in range(self.__height):
                for j in range(self.__width):
                    (xmin, xholemin, xholemax, xmax, ymin, yholemin, yholemax, ymax) = \
                        self.__getCoordinates(self.__height, self.__width, i, j)
                    maskpart = promptmask["mask"][yholemin:yholemax,xholemin:xholemax]
                    if maskpart.sum() > 0:
                        self.__activeTiles.append((promptmask["index"], i, j))
        print("active tiles:", self.__activeTiles)

    def __checkImageSizes(self):
        expectedImHeight = self.__height * 192
        expectedImWidth = self.__width * 192

        im = np.array(Image.open(os.path.join(self.__directory, "full.png")))
        assert im.shape[0] == expectedImHeight and im.shape[1] ==  expectedImWidth, \
            "full.png has wrong size."

        for promptmask in self.__promptmasks:
            assert promptmask["mask"].shape == (expectedImHeight, expectedImWidth, 1), \
                "Prompt mask '%s' has wrong size."%(promptmask["prompt"])

    def next(self):
        filenames = []
        for filename in os.listdir(self.__directory):
            if filename.startswith("full") and filename.endswith(".png"):
                filenames.append(filename)
     
        while self.__tileIndex < len(self.__activeTiles) and "full_%02i_%02i_%02i.png"%self.__activeTiles[self.__tileIndex] in filenames:
                self.__tileIndex += 1

        return self.__tileIndex < len(self.__activeTiles)


    def getHeight(self):
        return self.__height

    def getWidth(self):
        return self.__width                    
           
    def getPromptIndex(self):
        return self.__activeTiles[self.__tileIndex][0]

    def getI(self):
        return self.__activeTiles[self.__tileIndex][1]

    def getJ(self):
        return self.__activeTiles[self.__tileIndex][2]

    def getPromptmask(self):
        for promptmask in self.__promptmasks:
            if promptmask["index"] == self.getPromptIndex():
                return promptmask

    def __getCoordinates(self, height, width, i, j):
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

    def getCoordinates(self):
        tile = self.__activeTiles[self.__tileIndex]
        i = tile[1]
        j = tile[2]
        return self.__getCoordinates(self.__height, self.__width, i, j)

    def getCurrentFullFilename(self):
        tile = self.__activeTiles[self.__tileIndex]
        return "full_%02i_%02i_%02i.png"%tile

    def getLastFullFilename(self):
        if (self.__tileIndex == 0):
            return "full.png"
        else:
            tile = self.__activeTiles[self.__tileIndex - 1]
            return "full_%02i_%02i_%02i.png"%tile

    def getInitFilename(self):
        tile = self.__activeTiles[self.__tileIndex]
        return "init_%02i_%02i_%02i.png"%tile

    def getDirectory(self):
        return self.__directory 
