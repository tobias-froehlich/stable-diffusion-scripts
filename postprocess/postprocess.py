import numpy as np
from PIL import Image
import os
import sys
import tile
import utils
import threading
from Manager import Manager


assert len(sys.argv) == 2, "You must give exactly one argument: the directory."

directory = sys.argv[1]

im = np.array(Image.open(os.path.join(directory, "full.png")))

assert im.shape[0] % 192 == 0 and im.shape[1] % 192 == 0, \
    "The width and height of the image must be integer multiples of 192."

height = im.shape[0] // 192
width = im.shape[1] // 192


#for promptmask in promptmasks:
#    for i in range(0, height):
#        for j in range(width):



manager = Manager(directory, height, width)

exit = [False]

with open(os.path.join(directory, "parameters.txt"), "r") as f:
    parameters = f.read().strip()

print("Parameters: ", parameters)

def mainLoop(exit):
    while manager.next() and not exit[0]:
        tile.prepareInit(manager)
        promptmask = manager.getPromptmask()
        prefix = utils.launch("detailed high-resolution photography [painting] [drawing] " + promptmask["prompt"] + " -I" + manager.getInitFilename() + " --init_color " + manager.getInitFilename() + " " + parameters + " --outdir " + directory)
        tile.replaceOutput(manager, prefix)

    if exit[0]:
        print("Interrupted by user.")
    else:
        print("Finished. Enter quit.")

def userInputLoop(exit):

    while not exit[0]:
        i = input("Enter quit!\n")
        if i == "quit":
            exit[0] = True
            print("Wait until the current tile is processed!")

mainThread = threading.Thread(target=mainLoop, args=(exit,))
userInputThread = threading.Thread(target=userInputLoop, args=(exit,))

mainThread.start()
userInputThread.start()
mainThread.join()
userInputThread.join()
