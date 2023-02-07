from panda3d.core import *
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.directnotify import DirectNotifyGlobal
from toontown.distributed.DelayDeletable import DelayDeletable
import DistributedSuitBase
from toontown.battle.BattleProps import *
from direct.interval.IntervalGlobal import *
from libotp import *


class DistributedBossbotStatueSuit(DistributedSuitBase.DistributedSuitBase, DelayDeletable):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBossbotStatueSuit')

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
        except:
            self.DistributedSuit_initialized = 1
            DistributedSuitBase.DistributedSuitBase.__init__(self, cr)
            self.fsm = ClassicFSM.ClassicFSM('DistributedSuit', [State.State('Off', self.enterOff, self.exitOff, ['Walk', 'Battle']),
             State.State('Walk', self.enterWalk, self.exitWalk, ['WaitForBattle', 'Battle']),
             State.State('Battle', self.enterBattle, self.exitBattle, []),
             State.State('WaitForBattle', self.enterWaitForBattle, self.exitWaitForBattle, ['Battle'])], 'Off', 'Off')
            self.fsm.enterInitialState()

        return None

    def generate(self):
        DistributedSuitBase.DistributedSuitBase.generate(self)

    def announceGenerate(self):
        DistributedSuitBase.DistributedSuitBase.announceGenerate(self)
        self.setState('Walk')

    def disable(self):
        self.notify.debug('DistributedSuit %d: disabling' % self.getDoId())
        self.setState('Off')
        DistributedSuitBase.DistributedSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
        except:
            self.DistributedSuit_deleted = 1
            self.notify.debug('DistributedSuit %d: deleting' % self.getDoId())
            del self.fsm
            DistributedSuitBase.DistributedSuitBase.delete(self)

    def d_requestBattle(self, pos, hpr):
        self.cr.playGame.getPlace().setState('WaitForBattle')
        self.sendUpdate('requestBattle', [pos[0],
         pos[1],
         pos[2],
         hpr[0],
         hpr[1],
         hpr[2]])
        return None

    def __handleToonCollision(self, collEntry):
        toonId = base.localAvatar.getDoId()
        self.notify.debug('Distributed suit: requesting a Battle with ' + 'toon: %d' % toonId)
        self.d_requestBattle(self.getPos(), self.getHpr())
        self.setState('WaitForBattle')
        return None

    def enterWalk(self):
        self.setPos(3.04716, 0.0867744, 43)
        self.setScale(1.5)
        self.setY(-2)
        self.pose('golf-club-swing', 115)
        club = globalPropPool.getProp('golf-club')
        club.reparentTo(self.getRightHand())
        nameTag = self.find('**/def_nameTag')
        nameTag.hide()
        if base.localAvatar.defaultShard != 403000001:
            
            self.stone_music = base.loader.loadMusic('phase_12/audio/bgm/stone_cheese.ogg')
            base.playMusic(self.stone_music, looping=1, volume=0.9)
            
            cheeseAnimInterval = self.actorInterval("golf-club-swing",
                                            loop=0,
                                            startFrame=115,
                                            endFrame=0)
            
            
            self.mtrack1 = self.beginSupaFlyMove(Point3(3.04716, 0.0867744, 43), 0, 'toSky')
            self.mtrack2 = self.beginSupaFlyMove(Point3(316, 3, -2), 1, 'fromSky')
            
            battleSequence = Sequence(Wait(6),
                                    Wait(1),
                                    cheeseAnimInterval,
                                    Wait(1),
                                    Func(club.hide),
                                    Func(self.setScale, 1),
                                    Func(self.setH, -90),
                                    self.mtrack2,
                                    Func(self.loop, 'neutral'),
                                    Wait(2),
                                    Func(self.setChatAbsolute, "Don't you think I've aged well?", CFSpeech | CFTimeout),
                                    Wait(4),
                                    Func(self.setChatAbsolute, "Aging is my name, Executive Protection is my game.", CFSpeech | CFTimeout),
                                    Wait(4),
                                    Func(self.d_requestBattle, Point3(316, 3, -2), Vec3(0, 0, -90)))
            battleSequence.start()

    def exitWalk(self):
        return
