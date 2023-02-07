from otp.avatar import DistributedAvatarAI
from direct.distributed.ClockDelta import *

class DistributedBoilerAI(DistributedAvatarAI.DistributedAvatarAI):
    notify = directNotify.newCategory('DistributedBoilerAI')
    doId = 0

    def __init__(self, air):
        self.air = air
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        self.toonIds = []
        self.mode = 'neutral'
    
    def d_appendToonIds(self, toonId):
        self.toonIds.append(toonId)
    
    def setMode(self, mode):
        self.mode = mode
    
    def getMode(self):
        return self.mode
    
    def getToonIds(self):
        return self.toonIds