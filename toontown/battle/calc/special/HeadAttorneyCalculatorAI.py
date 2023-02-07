import math

from toontown.battle.SuitBattleGlobals import *
from toontown.battle.calc.BattleCalculatorGlobals import APPLY_HEALTH_ADJUSTMENTS
from toontown.battle.calc.SuitCalculatorAI import SuitCalculatorAI


class SuitSpecialCalculatorAI(SuitCalculatorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('HeadAttorneyCalculatorAI')

    def __init__(self, battle, suit, healCalculator):
        SuitCalculatorAI.__init__(self, battle, suit, healCalculator)
        self.suit = suit
        self.accept('suit-took-combo', self.__againstCombo)
        
    
    def __againstCombo(self):
        movie = [self.suit.doId, 4, 0, [24, 24, 24, 24], 0, 0, 0]
        self.battle.suitAttacks.append(movie)
