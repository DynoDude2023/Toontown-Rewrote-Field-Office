from direct.showbase.DirectObject import DirectObject

from toontown.battle.calc.BattleCalculatorGlobals import *


class BattleListenerAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleListenerAI')

    def __init__(self, battle, statusCalculator, healCalculator, squirtCalculator, trapCalculator):
        DirectObject.__init__(self)
        self.battle = battle
        self.toonHPAdjusts = {}  # Keeps track of healing amount for the current turn
        self.statusCalculator = statusCalculator
        self.healCalculator = healCalculator
        self.trapCalculator = trapCalculator
        self.squirtCalculator = squirtCalculator
        self.accept('toon-hp-change', self.__handleToonHeal, [])
    
    
    def __handleToonHeal(self):        
        print('Toon Heal Tracked')