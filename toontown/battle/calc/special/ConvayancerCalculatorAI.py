import math

from toontown.battle.SuitBattleGlobals import *
from toontown.battle.calc.BattleCalculatorGlobals import APPLY_HEALTH_ADJUSTMENTS
from toontown.battle.calc.SuitCalculatorAI import SuitCalculatorAI


class SuitSpecialCalculatorAI(SuitCalculatorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('ConvayancerCalculatorAI')

    def __init__(self, battle, suit, healCalculator):
        SuitCalculatorAI.__init__(self, battle, suit, healCalculator)
        self.suit = suit
        self.accept('suit-has-attacked', self.__healBack)
        
    
    def __healBack(self):
        movie = [self.suit.doId, 4, 0, [0, 0, 0, 0], 0, 0, 0]
        self.battle.suitAttacks.append(movie)
