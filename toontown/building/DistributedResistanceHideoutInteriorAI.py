from toontown.toonbase.ToontownGlobals import *
from otp.ai.AIBaseGlobal import *
from direct.distributed.ClockDelta import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.distributed import DistributedObjectAI
from direct.fsm import State
from toontown.toon import NPCToons

class DistributedResistanceHideoutInteriorAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, block, air, zoneId, building):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.block = block
        self.zoneId = zoneId
        self.building = building
        self.npcs = NPCToons.createNpcsInZone(air, zoneId)
        self.fsm = ClassicFSM.ClassicFSM('DistributedResistanceHideoutInteriorAI', [State.State('toon', self.enterToon, self.exitToon, ['beingTakenOver']), State.State('beingTakenOver', self.enterBeingTakenOver, self.exitBeingTakenOver, []), State.State('off', self.enterOff, self.exitOff, [])], 'toon', 'off')
        self.fsm.enterInitialState()

    def delete(self):
        self.ignoreAll()
        for npc in self.npcs:
            npc.requestDelete()

        del self.npcs
        del self.fsm
        del self.building
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def getZoneIdAndBlock(self):
        r = [self.zoneId, self.block]
        return r

    def getToonData(self):
        if not self.building.savedBy:
            # We cannot pack "None" to Astron,
            # so we'll pack an empty array instead.
            return []
        return self.building.savedBy

    def getState(self):
        r = [self.fsm.getCurrentState().getName(), globalClockDelta.getRealNetworkTime()]
        return r

    def setState(self, state):
        self.sendUpdate('setState', [state, globalClockDelta.getRealNetworkTime()])
        self.fsm.request(state)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterToon(self):
        pass

    def exitToon(self):
        pass

    def enterBeingTakenOver(self):
        pass

    def exitBeingTakenOver(self):
        pass