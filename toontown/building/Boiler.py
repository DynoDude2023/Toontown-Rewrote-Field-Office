from direct.actor import Actor
from otp.avatar import Avatar
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from libotp import *

#make a class called Boiler based on Avatar

boilerAnims = ['idle', 'intro', 'offenseAttack', 'hitThrow', 'defenseIntoOffense', 'offenseIdle']

class Boiler(Avatar.Avatar):
    
    def __init__(self):
        Avatar.Avatar.__init__(self)
        self.makeActor()
        self.makeAnimations()
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.setPickable(1)
        self.setName("The Boiler")
    
    def makeActor(self):
        #load the boiler model
        self.loadModel('phase_5/models/char/ttr_r_chr_cbg_boss')
        
        
    def makeAnimations(self):
        animBase = 'phase_5/models/char/ttr_a_chr_cbg_boss_'
        
        for anim in boilerAnims:
            self.loadAnims({anim:animBase + anim + '.bam'})
        
        self.setBlend(frameBlend = True)
        self.loop('idle')