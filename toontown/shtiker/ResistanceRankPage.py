import ShtikerPage
from toontown.toonbase import ToontownBattleGlobals
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class ResistanceRankPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.currentTrackInfo = None
        self.onscreen = 0
        self.lastInventoryTime = globalClock.getRealTime()
        self.gui = None
        return

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.title = DirectLabel(parent=self, relief=None, text="Resistance Rank", text_scale=0.12, textMayChange=1, pos=(0, 0, 0.62))
        self.guiMain = loader.loadModel('phase_3.5/models/gui/ttr_m_gui_sbk_resistanceRank')
        self.gui = self.guiMain.find('**/resistanceRank/geometry/background_grp')
        self.gui.reparentTo(hidden)
        self.gui.setScale(0.15)
        return

    def unload(self):
        del self.title
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        self.gui.reparentTo(aspect2dp)
        base.localAvatar.inventory.setActivateMode('book')

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)
        self.gui.reparentTo(hidden)
        return

