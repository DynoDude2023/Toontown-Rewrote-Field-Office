#make a class that inherits from DistributedObject called DistributedResistanceHideoutPipeAI

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals

class DistributedResistanceHideoutPipeAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedResistanceHideoutPipeAI')
    
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.air = air