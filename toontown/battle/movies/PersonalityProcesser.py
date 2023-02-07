from direct.interval.IntervalGlobal import *

class PersonalityProcesser():
    
    def __init__(self, battle, suit):
        self.battle = battle
        self.suit = suit
        
        self.lawbots = ['bf', 'b', 'dt', 'ac', 'bs', 'sd', 'le', 'bw', 'pf', 'shy', 'br', 'cv', 'sg', 'cm', 'nn', 'avo', 'f']
    
    def refreshProcesser(self, suit):
        #get the suit's head and if the suit is under 35% health, make the head loop 'neutral-hurt' else loop 'neutral'
        
        suitHeads = self.suit.getHeadParts()
        if suit.dna.name in self.lawbots:
            for suitHead in suitHeads:
                if self.suit.getHP() < self.suit.getMaxHP() * 0.35:
                    suitHead.loop('neutral-hurt')
                else:
                    suitHead.loop('neutral')
    
    def suitHeadAnimInterval(self, suit, anim):
        suitHeads = suit.getHeadParts()
        suitHeadsAnimInterval = Sequence()
        if suit.dna.name in self.lawbots:
            for suitHead in suitHeads:
                #find out the duration of the animation we want to play
                self.animationDuration = suitHead.getDuration(anim)
                suitHeadsAnimInterval.append(ActorInterval(suitHead, anim, duration=self.animationDuration))
        return suitHeadsAnimInterval
    
    def suitHeadAnimIntervalLoop(self, suit, anim):
        suitHeads = suit.getHeadParts()
        suitHeadsAnimInterval = Sequence()
        if suit.dna.name in self.lawbots:
            for suitHead in suitHeads:
                #find out the duration of the animation we want to play
                suitHead.loop(anim)