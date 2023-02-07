#make a class that inherits from DistributedObject call it DistributedBoiler

from otp.avatar import DistributedAvatar
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.directtools.DirectGeometry import CLAMP
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.distributed.ClockDelta import *
from libotp import *
from otp.otpbase import OTPGlobals
import Boiler

class DistributedBoiler(DistributedAvatar.DistributedAvatar, Boiler.Boiler):
    notify = directNotify.newCategory('DistributedBoiler')
    Id = 0

    def __init__(self, cr):
        DistributedAvatar.DistributedAvatar.__init__(self, cr)
        Boiler.Boiler.__init__(self)
        self.cr = cr
        self.toonIds = []
        self.mode = 'neutral'
        self.loop('idle')
        self.setBlend(frameBlend = True)
        
    def appendToonIds(self, toonId):
        self.toonIds.append(toonId)
    
    def parentBoiler(self, parent):
        self.reparentTo(parent)
    
    def getToonIds(self):
        return self.toonIds
    
    def setMode(self, mode):
        self.mode = mode
    
    def getMode(self):
        return self.mode
    
    def showHpText(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))

                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(4)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)

                self.hpText.setPos(0, 0, 5)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, 20), blendType='easeOut'), Wait(0.85), self.hpText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1), Func(self.hideHpText))
                seq.start()

    def hideHpText(self):
        DistributedAvatar.DistributedAvatar.hideHpText(self)