import math

from toontown.battle.SuitBattleGlobals import *
from toontown.battle.calc.BattleCalculatorGlobals import APPLY_HEALTH_ADJUSTMENTS
from toontown.battle.calc.SuitCalculatorAI import SuitCalculatorAI


class SuitSpecialCalculatorAI(SuitCalculatorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BoilerCalculator')

    def __init__(self, battle, suit, healCalculator):
        SuitCalculatorAI.__init__(self, battle, suit, healCalculator)
        self.suit = suit
        self.isOffense = 0
        self.isDefense = 0
        self.round = 0
        self.battle = battle
    
    def calcSuitAttack(self):
        SuitCalculatorAI.calcSuitAttack(self)
        self.round += 1
        if not self.isOffense and self.round == 1:
            movie = [self.suit.doId, 1, 0, [0, 0, 0, 0], 0, 0, 0]
            self.battle.suitAttacks.append(movie)
            self.isOffense = 1
        elif self.isOffense and self.round == 6:
            self.isOffense = 0
            self.round = 0
    