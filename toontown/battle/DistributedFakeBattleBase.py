from direct.actor import Actor
from direct.distributed import DistributedNode
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task

from toontown.battle.movies import MovieUtil, Movie, BattleProps, BattleParticles, PersonalityProcesser
from BattleBase import *
from otp.avatar import Emote
from toontown.distributed import DelayDelete
from toontown.hood import ZoneUtil
from toontown.Suit import Suit
from toontown.toonbase.ToonBaseGlobal import *


class DistributedFakeBattleBase(DistributedNode.DistributedNode, BattleBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFaKEBattleBase')
    id = 0
    camPos = ToontownBattleGlobals.BattleCamDefaultPos
    camHpr = ToontownBattleGlobals.BattleCamDefaultHpr
    camFov = ToontownBattleGlobals.BattleCamDefaultFov
    camMenuFov = ToontownBattleGlobals.BattleCamMenuFov
    camJoinPos = ToontownBattleGlobals.BattleCamJoinPos
    camJoinHpr = ToontownBattleGlobals.BattleCamJoinHpr

    def __init__(self, cr, townBattle):
        DistributedNode.DistributedNode.__init__(self, cr)
        NodePath.__init__(self)
        self.assign(render.attachNewNode(self.uniqueBattleName('distributed-fake-battle')))
        BattleBase.__init__(self)
        self.bossBattle = 0
        self.townBattle = townBattle
        self.__battleCleanedUp = 0
        self.activeIntervals = {}
        self.localToonJustJoined = 0
        self.choseAttackAlready = 0
        self.toons = []
        self.exitedToons = []
        self.fakeSuitTraps = ''
        self.membersKeep = None
        self.faceOffName = self.uniqueBattleName('faceoff')
        self.localToonBattleEvent = self.uniqueBattleName('localtoon-battle-event')
        self.adjustName = self.uniqueBattleName('adjust')
        self.timerCountdownTaskName = self.uniqueBattleName('timer-countdown')
        self.timer = Timer()
