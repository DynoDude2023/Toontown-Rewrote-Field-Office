from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase.ToontownGlobals import *
from toontown.battle.SuitBattleGlobals import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
import string
from direct.gui import OnscreenText
from toontown.battle import BattleBase

class PlayByPlayText(OnscreenText.OnscreenText):
    notify = DirectNotifyGlobal.directNotify.newCategory('PlayByPlayText')

    def __init__(self):
        OnscreenText.OnscreenText.__init__(self, mayChange=1, pos=(0.0, 0.75), scale=TTLocalizer.PBPTonscreenText, fg=(1, 0, 0, 1), font=getSignFont(), wordwrap=13)

    def getShowInterval(self, text, duration):
        return Sequence(Func(self.hide), Func(self.setFg, (1., 0., 0., 1.0)), Wait(duration * 0.3), Func(self.setText, text), Func(self.show), Wait(duration * 0.7), Func(self.hide))

    def getShowIntervalCheat(self, text, duration):
        return Sequence(Func(self.hide), Func(self.setFg, (1, 0.5, 0.0, 1.0)), Wait(duration * 0.3), Func(self.setText, text), Func(self.show), Wait(duration * 0.7), Func(self.hide))

    def getShowIntervalDesc(self, text, duration):
        return Sequence(Func(self.hide), Func(self.setWordwrap, None), Func(self.setPos, 0.0, 0.65), Func(self.setScale, 0.1), Func(self.setFg, (1, 1.0, 0.0, 1.0)), Wait(duration * 0.3), Func(self.setText, text), Func(self.show), Wait(duration * 0.7), Func(self.hide))

    def getToonsDiedInterval(self, textList, duration):
        track = Sequence(Func(self.hide), Wait(duration * 0.3))
        waitGap = 0.6 / len(textList) * duration
        for text in textList:
            newList = [Func(self.setText, text),
             Func(self.show),
             Wait(waitGap),
             Func(self.hide)]
            track += newList

        track.append(Wait(duration * 0.1))
        return track

