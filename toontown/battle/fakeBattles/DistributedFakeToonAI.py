#create a class called DistributedFakeToonAI that inherits from DistributedObjectAI

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals, ToontownBattleGlobals

class DistributedFakeToonAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFakeToonAI')
    
    def __init__(self, air, toonNpcId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.toonNpcId = toonNpcId
        self.createToonOBJ(toonNpcId)
    
    def createToonOBJ(self, npcId):
        self.sendUpdate('createNPCToon', [npcId])
    
    
    