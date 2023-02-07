#create a class called DistributedFakeToon that inherits from DistributedObject

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals, ToontownBattleGlobals
from avatar import ToontownAvatarUtils as AvatarUtils
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class DistributedFakeToon(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFakeToon')
    
    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
    
    def createNPCToon(self, npcId):
        AvatarUtils.createToon(npcId)
        
    
    