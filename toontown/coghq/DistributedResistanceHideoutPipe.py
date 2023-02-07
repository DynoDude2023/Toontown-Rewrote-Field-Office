#make a class that inherits from DistributedObject called DistributedResistanceHideoutPipe
from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil
from direct.interval.IntervalGlobal import *


class DistributedResistanceHideoutPipe(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedResistanceHideoutPipe')
    
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        #when the player touches the col_trigger collision on the pipe, the pipe will call the function onTrigger()
        self.cr = cr
        self.accept('enter' + 'col_trigger', self.onTrigger)
        
        self.notify.debug('__init__')
        self.loadModel()
    
    def loadModel(self):
        self.pipeModel = loader.loadModel('phase_9/models/cogHQ/ttr_r_ara_gen_sewerCap')
        self.pipeModel.reparentTo(render)
        if base.localAvatar.zoneId == 11000:
            self.pipeModel.setPos(48, -94.7, 0.287)
        else:
            self.pipeModel.setPos(250, -73, -68.367)
        self.pipeModel.setH(-200)
    
    '''
    def onTrigger(self, collEntry):
        #request a teleport to the resistance hideout
        zoneId = 11800
        base.cr.playGame.getPlace().fsm.request('teleportOut', [{'loader': ZoneUtil.getLoaderName(11000),
                                         'where': ZoneUtil.getToonWhereName(zoneId),
                                         'how': 'teleportIn',
                                         'hoodId': 11000,
                                         'zoneId': zoneId,
                                         'shardId': None,
                                         'avId': -1}])
        posSeq = Sequence(Func(base.transitions.irisOut, 2), Wait(7), Func(base.localAvatar.setPos, 66, 75, -21.970), Func(base.localAvatar.setH, -61), Func(base.transitions.irisIn, 2)).start()
    '''
    
    def onTrigger(self, collEntry):
        #request a teleport to the Lawbot Security Station
        if base.localAvatar.zoneId == 11000:
            self.teleport2()
        elif base.localAvatar.zoneId == 13000:
            self.teleport1()
        else:
            self.teleport1()
    
    def teleport1(self):
        zoneId = 13700
        base.cr.playGame.getPlace().fsm.request('teleportOut', [{'loader': ZoneUtil.getLoaderName(13000),
                                         'where': ZoneUtil.getToonWhereName(zoneId),
                                         'how': 'teleportIn',
                                         'hoodId': 13000,
                                         'zoneId': zoneId,
                                         'shardId': None,
                                         'avId': -1}])
        posSeq = Sequence(Func(base.transitions.irisOut, 2), Wait(7), Func(base.localAvatar.setPos, 0, 0, 0), Func(base.localAvatar.setH, -61), Func(base.transitions.irisIn, 2)).start()    
    
    def teleport2(self):
        #request a teleport to the resistance hideout
        zoneId = 11800
        base.cr.playGame.getPlace().fsm.request('teleportOut', [{'loader': ZoneUtil.getLoaderName(11000),
                                         'where': ZoneUtil.getToonWhereName(zoneId),
                                         'how': 'teleportIn',
                                         'hoodId': 11000,
                                         'zoneId': zoneId,
                                         'shardId': None,
                                         'avId': -1}])
        posSeq = Sequence(Func(base.transitions.irisOut, 2), Wait(7), Func(base.localAvatar.setPos, 66, 75, -21.970), Func(base.localAvatar.setH, -61), Func(base.transitions.irisIn, 2)).start()