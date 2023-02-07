from math import ceil

from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger

from toontown.battle.calc.BattleCalculatorGlobals import *


class HealCalculatorAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('HealCalculatorAI')

    def __init__(self, battle, statusCalculator):
        DirectObject.__init__(self)
        self.battle = battle
        self.toonHPAdjusts = {}  # Keeps track of healing amount for the current turn
        self.statusCalculator = statusCalculator
        self.accept('init-round', self.__resetFields)
        self.accept('round-over', self.__removeSadToons)

    def cleanup(self):
        self.ignoreAll()

    def calcAttackResults(self, attack, toonId):
        _, atkLevel, atkHp = getActualTrackLevelHp(attack)
        targetList = createToonTargetList(self.battle, toonId)
        toon = self.battle.getToon(toonId)
        healing = doDamageCalc(atkLevel, HEAL, toon)
        if not attackHasHit(attack, suit=0):
            healing *= 0.2
        self.notify.debug('toon does ' + str(healing) + ' healing to toon(s)')

        toons = self.battle.activeToons

        healing /= len(targetList)
        self.notify.debug('Splitting heal among targets')

        results = [0 for _ in xrange(len(toons))]
        healedToons = 0
        for target in targetList:

            healedToons += self.getToonHp(target) > 0

            self.notify.debug('%d targets %s, result: %d' % (toonId, target, healing))

            if target not in toons:
                self.notify.debug("The toon is not accessible!")
                continue

            results[toons.index(target)] = healing
        attack[TOON_HP_COL] = results  # <--------  THIS IS THE ATTACK OUTPUT!
        return healedToons > 0

    def healToon(self, attack, healing, toonId, position):
        excess = 0
        if CAP_HEALS:
            toonHp = self.getToonHp(toonId)
            toonMaxHp = self.__getToonMaxHp(toonId)
            if toonHp + healing > toonMaxHp:
                excess = toonHp + healing - toonMaxHp
                healing -= self.excess
                attack[TOON_HP_COL][position] = healing
        self.toonHPAdjusts[toonId] += healing
        messenger.send('toon-healed', [attack, healing, toonId])
        return excess

    def hurtToon(self, attack, toon):
        position = self.battle.activeToons.index(toon)
        if attack[SUIT_HP_COL][position] <= 0:
            return
        toonHp = self.getToonHp(toon)
        if toonHp - attack[SUIT_HP_COL][position] <= 0:
            self.notify.debug('Toon %d has died, removing' % toon)
            attack[TOON_DIED_COL] = attack[TOON_DIED_COL] | 1 << position
        self.notify.debug('Toon %s takes %s damage' % (toon, attack[SUIT_HP_COL][position]))
        self.toonHPAdjusts[toon] -= attack[SUIT_HP_COL][position]
        self.notify.debug('Toon %s now has %s health' % (toon, self.getToonHp(toon)))

    def getToonHp(self, toonId):
        toon = self.battle.getToon(toonId)
        if toon and toonId in self.toonHPAdjusts:
            return toon.hp + self.toonHPAdjusts[toonId]
        else:
            return 0

    def __getToonMaxHp(self, toonId):
        toon = self.battle.getToon(toonId)
        if toon:
            return toon.maxHp
        else:
            return 0

    def __resetFields(self):
        self.toonHPAdjusts = {}
        for t in self.battle.activeToons:
            self.toonHPAdjusts[t] = 0

    def __removeSadToons(self):
        self.toonHPAdjusts = {}
        for t in self.battle.activeToons:
            self.toonHPAdjusts[t] = 0
