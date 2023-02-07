from direct.showbase.DirectObject import DirectObject

from toontown.battle.calc.BattleCalculatorGlobals import *
from toontown.toonbase.ToontownBattleGlobals import RAILROAD_LEVEL_INDEX


class TrapCalculatorAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('TrapCalculatorAI')

    def __init__(self, battle, statusCalculator):
        DirectObject.__init__(self)
        self.trappedSuits = []  # Keeps track of trapped suits over a longer period of time
        self.trapCollisions = []  # Keeps track of trap collisions for the current turn
        self.battle = battle
        self.statusCalculator = statusCalculator
        self.accept('init-round', self.__resetFields)

    def cleanup(self):
        self.ignoreAll()

    def calcAttackResults(self, attack, toonId):
        atkLevel = attack[TOON_LVL_COL]
        targetList = createToonTargetList(self.battle, toonId)
        suits = self.battle.activeSuits
        results = [0 for _ in xrange(len(suits))]
        trappedSuits = 0

        for target in targetList:
            result = 0
            if FIRST_TRAP_ONLY and self.getSuitTrapType(target) != NO_TRAP:
                self.__clearTrap(toonId)
            else:
                result = self.__trapSuit(target, atkLevel, toonId)

            trappedSuits += target.getHP() > 0

            self.notify.debug('%d targets %s, result: %d' % (toonId, target, result))

            if result != 0:
                if target not in suits:
                    self.notify.debug("The suit is not accessible!")
                    continue

                results[suits.index(target)] = result

        attack[TOON_HP_COL] = results  # <--------  THIS IS THE ATTACK OUTPUT!
        return trappedSuits > 0

    def getSuitTrapType(self, suit):
        suitId = suit.getDoId()
        trapStatus = suit.getStatus(TRAPPED_STATUS)
        if trapStatus:
            if suitId in self.trapCollisions:
                self.notify.debug('%s used to have a trap, but it was removed.' % suitId)
                return NO_TRAP
            else:
                self.notify.debug('%s is currently trapped!' % suitId)
                return trapStatus['level']
        else:
            self.notify.debug('%s has no trap.' % suitId)
            return NO_TRAP

    def removeTrapStatus(self, suit):
        if suit in self.trappedSuits:
            self.trappedSuits.remove(suit)
            self.statusCalculator.removeStatus(suit, statusName=TRAPPED_STATUS)

    def clearTrapCreator(self, creatorId, suit=None):
        if not suit:
            for suit in self.trappedSuits:
                trapStatus = suit.getStatus(TRAPPED_STATUS)
                if trapStatus['toon'] == creatorId:
                    trapStatus['toon'] = 0
            return
        trapStatus = suit.getStatus(TRAPPED_STATUS)
        if trapStatus:
            trapStatus['toon'] = 0

    @staticmethod
    def getTrapInfo(suit):
        if TRAPPED_STATUS in suit.statuses:
            trapStatus = suit.getStatus(TRAPPED_STATUS)
            attackLevel = trapStatus['level']
            attackDamage = trapStatus['damage']
            trapCreatorId = trapStatus['toon']
        else:
            attackLevel = NO_TRAP
            attackDamage = 0
            trapCreatorId = 0
        return attackDamage, attackLevel, trapCreatorId

    def __trapSuit(self, suit, trapLvl, attackerId):
        if suit.getStatus(TRAPPED_STATUS):
            self.__checkTrapConflict(suit.doId)
        else:
            self.__applyTrap(attackerId, suit, trapLvl)

        if suit.doId in self.trapCollisions:
            self.notify.debug('There were two traps that collided! Removing the traps now.')
            self.removeTrapStatus(suit)
            result = 0
        else:
            result = TRAPPED_STATUS in suit.statuses
        return result

    def __applyTrap(self, toonId, suit, trapLvl):
        toon = self.battle.getToon(toonId)
        damage = getTrapDamage(trapLvl, toon, suit)
        self.notify.debug('%s places a %s damage trap!' % (toonId, damage))
        if trapLvl < getHighestTargetLevel(self.battle):
            self.__addTrapStatus(suit, trapLvl, damage, toonId)
        else:
            self.__addTrapStatus(suit, trapLvl, damage)

    def __addTrapStatus(self, suit, level=-1, damage=0, toonId=-1):
        trapStatus = genSuitStatus(TRAPPED_STATUS)
        trapStatus['level'] = level
        trapStatus['damage'] = damage
        trapStatus['toon'] = toonId
        self.notify.debug('%s now has a level %d trap that deals %d damage.' % (suit.doId, level, damage))
        suit.b_addStatus(trapStatus)
        self.trappedSuits.append(suit)

    def __checkTrapConflict(self, suitId, allSuits=None):
        if suitId not in self.trapCollisions:
            self.trapCollisions.append(suitId)
        if allSuits:
            for suit in allSuits:
                if suit.getStatus(TRAPPED_STATUS) and suit.doId not in self.trapCollisions:
                    self.trapCollisions.append(suitId)

    def __clearTrap(self, attackIdx):
        self.notify.debug('clearing out toon attack for toon ' + str(attackIdx) + '...')
        self.battle.toonAttacks[attackIdx] = getToonAttack(attackIdx)
        longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
        for j in xrange(longest):
            self.battle.toonAttacks[attackIdx][TOON_HP_COL].append(-1)
            self.battle.toonAttacks[attackIdx][TOON_HPBONUS_COL].append(-1)
            self.battle.toonAttacks[attackIdx][TOON_KBBONUS_COL].append(-1)
        self.notify.debug('toon attack is now ' + repr(self.battle.toonAttacks[attackIdx]))

    def __resetFields(self):
        self.trapCollisions = []
