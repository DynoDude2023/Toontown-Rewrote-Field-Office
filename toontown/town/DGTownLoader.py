import TownLoader
import DGStreet
from toontown.suit import Suit

class DGTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DGStreet.DGStreet
        self.musicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DG_town.dna'
        self.hideoutMusicFile = 'phase_9/audio/bgm/ttr_s_ara_shq_resistanceHideout.ogg'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        
        self.hideOutMusic = base.loader.loadMusic(self.hideoutMusicFile)
        dnaFile = 'phase_8/dna/daisys_garden_' + str(self.canonicalBranchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)
