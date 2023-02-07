from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger

from toontown.battle.calc.BattleCalculatorGlobals import *

NextMarks = [0.1, 0.15, 0.18, 0.2]

class ThrowCalculatorAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ThrowCalculatorAI')

    def __init__(self, battle, statusCalculator):
        DirectObject.__init__(self)
        self.battle = battle
        self.markedSuits = []                       # Keeps track of marked suits over a longer period of time
        self.statusCalculator = statusCalculator
        self.accept('post-suit', self.__postSuitStatusRounds)

    def cleanup(self):
        self.ignoreAll()

    def calcAttackResults(self, attack, toonId):
        atkTrack, atkLevel, atkHp = getActualTrackLevelHp(attack)
        targetList = createToonTargetList(self.battle, toonId)
        suits = self.battle.activeSuits
        toon = self.battle.getToon(toonId)
        results = [0 for _ in xrange(len(suits))]
        targetsHit = 0
        for target in targetList:
            if target not in suits:
                self.notify.debug("The target is not accessible!")
                continue

            attackDamage = receiveDamageCalc(atkLevel, atkTrack, target, toon)

            targetsHit += target.getHP() > 0

            self.notify.debug('%d targets %s, result: %d' % (toonId, target, attackDamage))


            if target.dna.name == 'hat' and target.getStatus(LURED_STATUS):
                messenger.send('suit-took-combo')
            
            if target.getStatus(LURED_STATUS):
                
                messenger.send('delayed-wake', [toonId, target])
                messenger.send('lured-hit-exp', [attack, target])

            results[suits.index(target)] = attackDamage
        attack[TOON_HP_COL] = results  # <--------  THIS IS THE ATTACK OUTPUT!
        return targetsHit > 0


    def __postSuitStatusRounds(self):
        for activeSuit in self.battle.activeSuits:
            removedStatus = activeSuit.decStatusRounds(MARKED_STATUS)
            if removedStatus:
                self.removeMarkStatus(activeSuit, removedStatus)
