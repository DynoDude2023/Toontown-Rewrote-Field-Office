from otp.ai.AIBase import *
from BattleBase import *
from BattleCalculatorAI import *
from toontown.toonbase.ToontownBattleGlobals import *
import DistributedBattleBaseAI
from direct.task import Task
from SuitBattleGlobals import MAX_Suit_CAPACITY
from direct.directnotify import DirectNotifyGlobal
import random


class DistributedBattleAI(DistributedBattleBaseAI.DistributedBattleBaseAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleAI')

    def __init__(self, air, battleMgr, pos, fakeSuit, npcId, zoneId, finishCallback=None,
                 maxfakeSuits=4, tutorialFlag=0,
                 levelFlag=0, interactivePropTrackBonus=-1):
        DistributedBattleBaseAI.DistributedBattleBaseAI.__init__(self, air, zoneId, finishCallback, maxfakeSuits=maxfakeSuits,
                                                                 tutorialFlag=tutorialFlag,
                                                                 interactivePropTrackBonus=interactivePropTrackBonus)
        self.battleMgr = battleMgr
        self.pos = pos
        self.initialfakeSuitPos = fakeSuit.getConfrontPosHpr()[0]
        self.initialToonPos = fakeSuit.getConfrontPosHpr()[0]
        self.addfakeSuit(fakeSuit)
        self.avId = npcId
        if levelFlag == 0:
            self.addToon(npcId)
        self.faceOffToon = npcId
        self.fsm.request('FaceOff')

    def generate(self):
        DistributedBattleBaseAI.DistributedBattleBaseAI.generate(self)
        toon = simbase.air.doId2do.get(self.avId)
        if toon:
            if hasattr(self, 'doId'):
                toon.b_setBattleId(self.doId)
            else:
                toon.b_setBattleId(-1)
        self.avId = None
        return

    def faceOffDone(self):
        npcId = self.air.getAvatarIdFromSender()
        if self.ignoreFaceOffDone == 1:
            self.notify.debug('faceOffDone() - ignoring toon: %d' % npcId)
            return
        elif self.fsm.getCurrentState().getName() != 'FaceOff':
            self.notify.warning('faceOffDone() - in state: %s' % self.fsm.getCurrentState().getName())
            return
        elif self.toons.count(npcId) == 0:
            self.notify.warning('faceOffDone() - toon: %d not in toon list' % npcId)
            return
        self.notify.debug('toon: %d done facing off' % npcId)
        self.handleFaceOffDone()

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        self.joinableFsm.request('Joinable')
        self.runableFsm.request('Unrunable')
        self.fakeSuits[0].releaseControl()
        timeForFaceoff = self.calcFaceoffTime(self.pos, self.initialfakeSuitPos) + FACEOFF_TAUNT_T + SERVER_BUFFER_TIME
        if self.interactivePropTrackBonus >= 0:
            timeForFaceoff += FACEOFF_LOOK_AT_PROP_T
        self.timer.startCallback(timeForFaceoff, self.__serverFaceOffDone)
        return None

    def __serverFaceOffDone(self):
        self.notify.debug('faceoff timed out on server')
        self.ignoreFaceOffDone = 1
        self.handleFaceOffDone()

    def exitFaceOff(self):
        self.timer.stop()
        return None

    def handleFaceOffDone(self):
        self.timer.stop()
        self.activatefakeSuit(self.fakeSuits[0])
        if len(self.toons) == 0:
            self.b_setState('Resume')
        elif self.faceOffToon == self.toons[0]:
            self.activeToons.append(self.toons[0])
            self.sendEarnedExperience(self.toons[0])
        self.d_setMembers()
        self.b_setState('WaitForInput')

    def localMovieDone(self, needUpdate, deadToons, deadfakeSuits, lastActivefakeSuitDied):
        if len(self.toons) == 0:
            self.d_setMembers()
            self.b_setState('Resume')
        elif len(self.fakeSuits) == 0:
            for npcId in self.activeToons:
                toon = self.getToon(npcId)
                if toon:
                    self.toonItems[npcId] = self.air.questManager.recoverItems(toon, self.fakeSuitsKilled, self.zoneId)
                    if npcId in self.helpfulToons:
                        self.toonMerits[npcId] = self.air.promotionMgr.recoverMerits(toon, self.fakeSuitsKilled,
                                                                                      self.zoneId)
                    else:
                        self.notify.debug('toon %d not helpful, skipping merits' % npcId)

            self.d_setMembers()
            self.d_setBattleExperience()
            self.b_setState('Reward')
        else:
            if needUpdate == 1:
                self.d_setMembers()
                if len(deadfakeSuits) > 0 and lastActivefakeSuitDied == 0 or len(deadToons) > 0:
                    self.needAdjust = 1
            self.setState('WaitForJoin')

    def enterReward(self):
        self.notify.debug('enterReward()')
        self.joinableFsm.request('Unjoinable')
        self.runableFsm.request('Unrunable')
        self.resetResponses()
        self.assignRewards()
        self.startRewardTimer()

    def startRewardTimer(self):
        self.timer.startCallback(REWARD_TIMEOUT, self.serverRewardDone)

    def exitReward(self):
        return None

    def enterResume(self):
        self.notify.debug('enterResume()')
        self.joinableFsm.request('Unjoinable')
        self.runableFsm.request('Unrunable')
        DistributedBattleBaseAI.DistributedBattleBaseAI.enterResume(self)
        if self.finishCallback:
            self.finishCallback(self.zoneId)
        self.battleMgr.destroy(self)
