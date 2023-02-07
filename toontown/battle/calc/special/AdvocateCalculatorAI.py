import math

from toontown.battle.SuitBattleGlobals import *
from toontown.battle.calc.BattleCalculatorGlobals import APPLY_HEALTH_ADJUSTMENTS
from toontown.battle.calc.SuitCalculatorAI import SuitCalculatorAI


class SuitSpecialCalculatorAI(SuitCalculatorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('AdvocateCalculatorAI')

    def __init__(self, battle, suit, healCalculator):
        SuitCalculatorAI.__init__(self, battle, suit, healCalculator)
        self.suit = suit
        self.accept('suit-soaked', self.__againstSoak)
        
    
    def __againstSoak(self):
        movie = [self.suit.doId, 4, 0, [40, 0, 0, 0], 0, 0, 0]
        self.battle.suitAttacks.append(movie)
