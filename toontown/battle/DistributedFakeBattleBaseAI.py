from otp.ai.AIBase import *
from direct.distributed.ClockDelta import *
from BattleBase import *
import BattleCalculatorAI
from toontown.battle.calc.BattleCalculatorGlobals import TRAP_CONFLICT
from toontown.toonbase.ToontownBattleGlobals import *
from SuitBattleGlobals import *
from panda3d.core import *
import BattleExperienceAI
from direct.distributed import DistributedObjectAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task import Task
from direct.directnotify import DirectNotifyGlobal
from toontown.ai import DatabaseObject
from toontown.toon import DistributedToonAI
from toontown.toon import InventoryBase
from toontown.toonbase import ToontownGlobals
import random
from toontown.toon import NPCToons
from toontown.pets import DistributedPetProxyAI


class DistributedFakeBattleBaseAI(DistributedObjectAI.DistributedObjectAI, BattleBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleBaseAI')

    def __init__(self, air, zoneId, finishCallback=None, maxfakeSuits=4, bossBattle=0, tutorialFlag=0,
                 interactivePropTrackBonus=-1):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.serialNum = 0
        self.zoneId = zoneId
        self.maxfakeSuits = maxfakeSuits
        self.setBossBattle(bossBattle)
        self.tutorialFlag = tutorialFlag
        self.interactivePropTrackBonus = interactivePropTrackBonus
        self.finishCallback = finishCallback
        self.avatarExitEvents = []
        self.responses = {}
        self.adjustingResponses = {}
        self.joinResponses = {}
        self.adjustingfakeSuits = []
        self.adjustingToons = []
        self.numfakeSuitsEver = 0
        BattleBase.__init__(self)
        self.streetBattle = 1
        self.pos = Point3(0, 0, 0)
        self.initialfakeSuitPos = Point3(0, 0, 0)
