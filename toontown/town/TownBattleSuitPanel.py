from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import taskMgr

from toontown.battle import BattleProps
from toontown.suit.Suit import Suit
from toontown.suit.SuitAvatarPanel import SuitAvatarPanel
from toontown.toonbase.ToontownBattleGlobals import *


class TownBattleSuitPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleSuitPanel')
    healthColors = Suit.healthColors
    healthGlowColors = Suit.healthGlowColors

    def __init__(self, id):
        gui = loader.loadModel('phase_3.5/models/gui/ttr_m_gui_bat_cogGUI')
        DirectFrame.__init__(self, relief=None, image=gui,
                             image_color=Vec4(1, 1, 1, 1.0))
        self.hpText = DirectLabel(parent=self, text='', pos=(-0.06, 0, -0.0325), text_scale=0.045)
        self.hpText.hide()
        self.setScale(0.05)
        self.initialiseoptions(TownBattleSuitPanel)
        self.hidden = False
        self.cog = None
        self.isLoaded = 0
        self.notify.info("Loading Suit Battle Panel!")
        self.healthText = DirectLabel(parent=self, text='', pos=(0, 0, -0.075), text_scale=0.05)
        healthGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = gui.find('**/ttr_t_gui_bat_cogGUI_health_light_card')
        button.setColor(Vec4(0, 1, 0, 1))
        self.accept('inventory-levels', self.__handleToggle)
        self.healthNode = self.attachNewNode('health')
        button.reparentTo(self.healthNode)
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(button)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(Vec4(0.25, 1, 0.25, 0.5))
        self.button = button
        self.glow = glow
        self.head = None
        self.blinkTask = None
        self.hide()
        healthGui.removeNode()
        gui.removeNode()

    def setCogInformation(self, cog):
        self.cog = cog
        self.updateHealthBar()
        if self.head:
            self.head.removeNode()

        self.head = self.attachNewNode('head')
        for part in cog.headParts:
            copyPart = part.copyTo(self.head)
            copyPart.setDepthTest(1)
            copyPart.setDepthWrite(1)

        p1, p2 = Point3(), Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2])
        s = 0.1 / biggest
        self.head.setPosHprScale(0.1, 0, 0.01, 180, 0, 0, s, s, s)
        self.setLevelText()

    def setLevelText(self):
        
        TownBattleSuitLevel = 'Level %(level)s'
        self.healthText['text'] = TownBattleSuitLevel % {'level': (self.cog.getActualLevel())}
        

    def updateHealthBar(self):
        condition = self.cog.healthCondition
        if condition == 9:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        elif condition == 10:
            taskMgr.remove(self.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.uniqueName('blink-task'))
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)

            if not self.glow.isEmpty():
                self.glow.setColor(self.healthGlowColors[condition], 1)
        self.hp = self.cog.getHP()
        self.maxHp = self.cog.getMaxHP()
        self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)

    def show(self):    
        if self.cog:
            self.updateHealthBar()
        self.hidden = False
        self.healthNode.show()
        self.button.show()
        self.glow.show()
        DirectFrame.show(self)
    
    def __handleToggle(self):
        if self.cog:
            if self.hidden:
                self.show()
            else:
                self.hide()

    def __blinkRed(self, task):
        if not self.button.isEmpty():
            self.button.setColor(self.healthColors[8], 1)

        if not self.glow.isEmpty():
            self.glow.setColor(self.healthGlowColors[8], 1)

        return Task.done

    def __blinkGray(self, task):
        if not self.button.isEmpty():
            self.button.setColor(self.healthColors[9], 1)

        if not self.glow.isEmpty():
            self.glow.setColor(self.healthGlowColors[9], 1)

        return Task.done

    def hide(self):
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        self.hidden = True
        self.healthNode.hide()
        self.button.hide()
        self.glow.hide()
        DirectFrame.hide(self)

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        del self.glow
        del self.cog
        del self.button
        del self.blinkTask
        del self.hpText
        DirectFrame.destroy(self)

    def cleanup(self):
        self.ignoreAll()
        if self.head:
            self.head.removeNode()
            del self.head

        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        del self.blinkTask
        self.healthNode.removeNode()
        self.button.removeNode()
        self.glow.removeNode()
        DirectFrame.destroy(self)
