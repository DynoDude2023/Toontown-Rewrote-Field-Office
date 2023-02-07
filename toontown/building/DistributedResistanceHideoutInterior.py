from toontown.toonbase.ToonBaseGlobal import *
from panda3d.core import *
from panda3d.toontown import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
import ToonInterior
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.distributed import DistributedObject
from direct.fsm import State
import random
import ToonInteriorColors
from toontown.hood import ZoneUtil
from toontown.toon import ToonDNA
from toontown.toon import ToonHead
SIGN_LEFT = -4
SIGN_RIGHT = 4
SIGN_BOTTOM = -3.5
SIGN_TOP = 1.5
FrameScale = 1.4

class DistributedResistanceHideoutInterior(DistributedObject.DistributedObject):

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedResistanceHideoutInterior', [State.State('toon', self.enterToon, self.exitToon, ['beingTakenOver']), State.State('beingTakenOver', self.enterBeingTakenOver, self.exitBeingTakenOver, []), State.State('off', self.enterOff, self.exitOff, [])], 'toon', 'off')
        self.fsm.enterInitialState()

    def generate(self):
        DistributedObject.DistributedObject.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.setup()

    def disable(self):
        self.interior.removeNode()
        del self.interior
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        del self.fsm
        DistributedObject.DistributedObject.delete(self)

    def randomDNAItem(self, category, findFunc):
        codeCount = self.dnaStore.getNumCatalogCodes(category)
        index = self.randomGenerator.randint(0, codeCount - 1)
        code = self.dnaStore.getCatalogCode(category, index)
        return findFunc(code)

    def replaceRandomInModel(self, model):
        baseTag = 'random_'
        npc = model.findAllMatches('**/' + baseTag + '???_*')
        for i in xrange(npc.getNumPaths()):
            np = npc.getPath(i)
            name = np.getName()
            b = len(baseTag)
            category = name[b + 4:]
            key1 = name[b]
            key2 = name[b + 1]
            if key1 == 'm':
                model = self.randomDNAItem(category, self.dnaStore.findNode)
                newNP = model.copyTo(np)
                c = render.findAllMatches('**/collision')
                c.stash()
                if key2 == 'r':
                    self.replaceRandomInModel(newNP)
            elif key1 == 't':
                texture = self.randomDNAItem(category, self.dnaStore.findTexture)
                np.setTexture(texture, 100)
                newNP = np
            if key2 == 'c':
                if category == 'TI_wallpaper' or category == 'TI_wallpaper_border':
                    self.randomGenerator.seed(self.zoneId)
                    newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
                else:
                    newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        interior = loader.loadModel('phase_9/models/cogHQ/ttr_m_ara_shq_resistanceHideout')
        self.interior = interior.copyTo(render)
        
        
        doorModelName = 'door_double_round_ul'
        door_origin = self.interior.find('**/loc_bench')
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        doorNP = door.copyTo(door_origin)
        door_origin.setScale(0.8, 0.8, 0.8)
        door_origin.setPos(door_origin, 0, -0.025, 0)
    
        
        doorNP = door.copyTo(door_origin)
        
        color = Vec4(1, 1, 1, 1)
        
        DNADoor.setupDoor(doorNP, self.interior, door_origin, self.dnaStore, str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        
    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block

    def setToonData(self, savedBy):
        self.savedBy = savedBy

    def buildTrophy(self):
        if self.savedBy == None:
            return
        numToons = len(self.savedBy)
        pos = 1.25 - 1.25 * numToons
        trophy = hidden.attachNewNode('trophy')
        for avId, name, dnaNetString, isGM in self.savedBy:
            frame = self.buildFrame(name, dnaNetString)
            frame.reparentTo(trophy)
            frame.setPos(pos, 0, 0)
            pos += 2.5

        return trophy

    def buildFrame(self, name, dnaNetString):
        frame = loader.loadModel('phase_3.5/models/modules/trophy_frame')
        dna = ToonDNA.ToonDNA(dnaNetString)
        head = ToonHead.ToonHead()
        head.setupHead(dna)
        head.setPosHprScale(0, -0.05, -0.05, 180, 0, 0, 0.55, 0.02, 0.55)
        if dna.head[0] == 'r':
            head.setZ(-0.15)
        elif dna.head[0] == 'h':
            head.setZ(0.05)
        elif dna.head[0] == 'm':
            head.setScale(0.45, 0.02, 0.45)
        head.reparentTo(frame)
        nameText = TextNode('trophy')
        nameText.setFont(ToontownGlobals.getToonFont())
        nameText.setAlign(TextNode.ACenter)
        nameText.setTextColor(0, 0, 0, 1)
        nameText.setWordwrap(5.36 * FrameScale)
        nameText.setText(name)
        namePath = frame.attachNewNode(nameText.generate())
        namePath.setPos(0, -0.03, -.6)
        namePath.setScale(0.186 / FrameScale)
        frame.setScale(FrameScale, 1.0, FrameScale)
        return frame

    def setState(self, state, timestamp):
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterToon(self):
        pass

    def exitToon(self):
        pass

    def enterBeingTakenOver(self, ts):
        messenger.send('clearOutToonInterior')

    def exitBeingTakenOver(self):
        pass
