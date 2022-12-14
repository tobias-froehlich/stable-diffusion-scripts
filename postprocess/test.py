import tile
import utils
from Manager import Manager

height = 7
width = 10



#for promptmask in promptmasks:
#    for i in range(0, height):
#        for j in range(width):

manager = Manager(height, width)

while manager.next():
    tile.prepareInit(manager)
    promptmask = manager.getPromptmask()
    prefix = utils.launch("detailed high-resolution photography [painting] [drawing] " + promptmask["prompt"] + " -I" + manager.getInitFilename() + " -s10 -f0.3 ")
    tile.replaceOutput(manager, prefix)
