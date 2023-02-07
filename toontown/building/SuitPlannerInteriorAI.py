from otp.ai.AIBaseGlobal import *
import random
from toontown.suit import SuitDNA
from direct.directnotify import DirectNotifyGlobal
from toontown.suit import DistributedSuitAI
import SuitBuildingGlobals, types

class SuitPlannerInteriorAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitPlannerInteriorAI')

    def __init__(self, numFloors, bldgLevel, bldgTrack, zone, respectInvasions=1):
        self.dbg_nSuits1stRound = config.GetBool('n-suits-1st-round', 0)
        self.dbg_4SuitsPerFloor = config.GetBool('4-suits-per-floor', 0)
        self.dbg_1SuitPerFloor = config.GetBool('1-suit-per-floor', 0)
        self.zoneId = zone
        self.numFloors = numFloors
        self.respectInvasions = respectInvasions
        dbg_defaultSuitName = simbase.config.GetString('suit-type', 'random')
        if dbg_defaultSuitName == 'random':
            self.dbg_defaultSuitType = None
        else:
            self.dbg_defaultSuitType = SuitDNA.getSuitType(dbg_defaultSuitName)
        if isinstance(bldgLevel, types.StringType):
            self.notify.warning('bldgLevel is a string!')
            bldgLevel = int(bldgLevel)
        self._genSuitInfos(numFloors, bldgLevel, bldgTrack)
        return

    def __genJoinChances(self, num):
        joinChances = []
        for currChance in xrange(num):
            joinChances.append(random.randint(1, 100))

        joinChances.sort(cmp)
        return joinChances


    def _genSuitInfos(self, numFloors, bldgLevel, bldgTrack):
        self.suitInfos = []
        self.notify.debug('\n\ngenerating suitsInfos with numFloors (' + str(numFloors) + ') bldgLevel (' + str(bldgLevel) + '+1) and bldgTrack (' + str(bldgTrack) + ')')
        extraTracks = ['s', 'm', 'l']
        for currFloor in xrange(numFloors):
            infoDict = {}
            lvls = self.__genLevelList(bldgLevel, currFloor, numFloors)
            activeDicts = []
            maxActive = min(4, len(lvls))
            if self.dbg_nSuits1stRound:
                numActive = min(self.dbg_nSuits1stRound, maxActive)
            else:
                numActive = random.randint(1, maxActive)
            if currFloor + 1 == numFloors and len(lvls) > 1:
                origBossSpot = len(lvls) - 1
                if numActive == 1:
                    newBossSpot = numActive - 1
                else:
                    newBossSpot = numActive - 2
                tmp = lvls[newBossSpot]
                lvls[newBossSpot] = lvls[origBossSpot]
                lvls[origBossSpot] = tmp
            bldgInfo = SuitBuildingGlobals.SuitBuildingInfo[bldgLevel]
            if len(bldgInfo) > SuitBuildingGlobals.SUIT_BLDG_INFO_REVIVES:
                revives = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_REVIVES][0]
            else:
                revives = 0
            for currActive in xrange(numActive - 1, -1, -1):
                level = lvls[currActive]

                activeDict = {}

                if bldgTrack == 'x':
                    activeDict['track'] = random.choice(['s', 'm', 'l', 'c'])
                else:
                    activeDict['track'] = bldgTrack
                if activeDict['track'] in extraTracks:
                    type = self.__genExtraSuitType(level)
                else:
                    type = self.__genNormalSuitType(level)
                activeDict['type'] = type
                activeDict['level'] = level
                if revives == 2:
                    activeDict['revives'] = random.randint(0, 1)
                else:
                    activeDict['revives'] = revives
                activeDicts.append(activeDict)

            infoDict['activeSuits'] = activeDicts
            reserveDicts = []
            numReserve = len(lvls) - numActive
            joinChances = self.__genJoinChances(numReserve)
            for currReserve in xrange(numReserve):
                level = lvls[currReserve + numActive]
                reserveDict = {}
                if bldgTrack == 'x':
                    reserveDict['track'] = random.choice(['s', 'm', 'l', 'c'])
                else:
                    reserveDict['track'] = bldgTrack
                if reserveDict['track'] in extraTracks:
                    type = self.__genExtraSuitType(level)
                else:
                    type = self.__genNormalSuitType(level)
                reserveDict['type'] = type
                reserveDict['level'] = level
                if revives == 2:
                    reserveDict['revives'] = random.randint(0, 1)
                else:
                    reserveDict['revives'] = revives
                reserveDict['joinChance'] = joinChances[currReserve]
                reserveDicts.append(reserveDict)

            infoDict['reserveSuits'] = reserveDicts
            self.suitInfos.append(infoDict)

    def __genNormalSuitType(self, lvl):
        if self.dbg_defaultSuitType != None:
            return self.dbg_defaultSuitType
        return SuitDNA.getRandomSuitType(lvl)

    def __genExtraSuitType(self, lvl):
        if self.dbg_defaultSuitType != None:
            return self.dbg_defaultSuitType
        return SuitDNA.getRandomSuitTypeExtra(lvl)

    def __genLevelList(self, bldgLevel, currFloor, numFloors):
        bldgInfo = SuitBuildingGlobals.SuitBuildingInfo[bldgLevel]
        if self.dbg_1SuitPerFloor:
            return [1]
        else:
            if self.dbg_4SuitsPerFloor:
                return [5, 6, 7, 10]
        lvlPoolRange = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_LVL_POOL]
        maxFloors = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_FLOORS][1]
        lvlPoolMults = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_LVL_POOL_MULTS]
        floorIdx = min(currFloor, maxFloors - 1)
        lvlPoolMin = lvlPoolRange[0] * lvlPoolMults[floorIdx]
        lvlPoolMax = lvlPoolRange[1] * lvlPoolMults[floorIdx]
        lvlPool = random.randint(int(lvlPoolMin), int(lvlPoolMax))
        lvlMin = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_SUIT_LVLS][0]
        lvlMax = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_SUIT_LVLS][1]
        self.notify.debug('Level Pool: ' + str(lvlPool))
        lvlList = []
        while lvlPool >= lvlMin:
            newLvl = random.randint(lvlMin, min(lvlPool, lvlMax))
            lvlList.append(newLvl)
            lvlPool -= newLvl

        if currFloor + 1 == numFloors:
            bossLvlRange = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_BOSS_LVLS]
            newLvl = random.randint(bossLvlRange[0], bossLvlRange[1])
            lvlList.append(newLvl)
        lvlList.sort(cmp)
        self.notify.debug('LevelList: ' + repr(lvlList))
        return lvlList

    def __setupSuitInfo(self, suit, bldgTrack, suitLevel, suitType, suitName=None):
        suitName, skeleton = simbase.air.suitInvasionManager.getInvadingCog()
        if suitName and self.respectInvasions:
            suitType = SuitDNA.getSuitType(suitName)
            bldgTrack = SuitDNA.getSuitDept(suitName)
            suitLevel = min(max(suitLevel, suitType), suitType + 7)
        dna = SuitDNA.SuitDNA()
        if suitName:
            dna.newSuit(suitName)
        else:
            dna.newSuitRandom(suitType, bldgTrack)
        suit.dna = dna
        self.notify.debug('Creating suit type ' + suit.dna.name + ' of level ' + str(suitLevel) + ' from type ' + str(suitType) + ' and track ' + str(bldgTrack))
        suit.setLevel(suitLevel)
        return skeleton

    def __genSuitObject(self, suitZone, suitType, bldgTrack, suitLevel, revives=0, suitName=None):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        skel = self.__setupSuitInfo(newSuit, bldgTrack, suitLevel, suitType, suitName=suitName)
        newSuit.setSkeleRevives(revives)
        newSuit.generateWithRequired(suitZone)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        if skel:
            if skel == 2:
                newSuit.b_setSkeleRevives(1)
            elif skel == 1:
                suit.setSkelecog(1)
            else:
                pass
        return newSuit
    
    def __setupSuitInfo2(self, suit, bldgTrack, suitLevel, suitType, suitName=None):
        dna = SuitDNA.SuitDNA()
        dna.newSuit('bo')
        suit.dna = dna
        self.notify.debug('Creating suit type ' + suit.dna.name + ' of level ' + str(suitLevel) + ' from type ' + str(suitType) + ' and track ' + str(bldgTrack))
        suit.setLevel(1)

    def __genSuitObject2(self, suitZone, suitType, bldgTrack, suitLevel, revives=0, suitName=None):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        skel = self.__setupSuitInfo2(newSuit, bldgTrack, suitLevel, suitType, suitName=suitName)
        newSuit.setSkeleRevives(revives)
        newSuit.generateWithRequired(suitZone)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        if skel:
            if skel == 2:
                newSuit.b_setSkeleRevives(1)
            elif skel == 1:
                suit.setSkelecog(1)
            else:
                pass
        return newSuit

    def myPrint(self):
        self.notify.info('Generated suits for building: ')
        for currInfo in suitInfos:
            whichSuitInfo = suitInfos.index(currInfo) + 1
            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[0])) + ' active suits.')
            for currActive in xrange(len(currInfo[0])):
                self.notify.debug('  Active suit ' + str(currActive + 1) + ' is of type ' + str(currInfo[0][currActive][0]) + ' and of track ' + str(currInfo[0][currActive][1]) + ' and of level ' + str(currInfo[0][currActive][2]))

            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[1])) + ' reserve suits.')
            for currReserve in xrange(len(currInfo[1])):
                self.notify.debug('  Reserve suit ' + str(currReserve + 1) + ' is of type ' + str(currInfo[1][currReserve][0]) + ' and of track ' + str(currInfo[1][currReserve][1]) + ' and of lvel ' + str(currInfo[1][currReserve][2]) + ' and has ' + str(currInfo[1][currReserve][3]) + '% join restriction.')

    def genFloorSuits(self, floor):
        suitHandles = {}
        floorInfo = self.suitInfos[floor]
        activeSuits = []
        
        for i in xrange(4):
            newSuitType = random.randint(1, 8)
            level = random.randint(newSuitType, newSuitType+7)
            if level > newSuitType+7:
                level = newSuitType+7
            elif level < 7:
                level = 7
            suit = self.__genSuitObject(self.zoneId, newSuitType, 's', level, 0)
            activeSuits.append(suit)
        
        
        
        suitHandles['activeSuits'] = activeSuits
        reserveSuits = []
        for i in xrange(10):
            newSuitType = random.randint(1, 8)
            level = random.randint(newSuitType, newSuitType+7)
            if level > newSuitType+7:
                level = newSuitType+7
            elif level < 7:
                level = 7
            suit = self.__genSuitObject(self.zoneId, newSuitType, 's', level, 0)
            reserveSuits.append((suit, 100))

        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles
    
    def genFloorSuits2(self, floor):
        suitHandles = {}
        floorInfo = self.suitInfos[floor]
        activeSuits = []


        suit5 = self.__genSuitObject2(self.zoneId, 1, 's', 1, 0, suitName='bo')
        activeSuits.append(suit5)


        suitHandles['activeSuits'] = activeSuits
        reserveSuits = []
        for i in xrange(10):
            newSuitType = random.randint(1, 8)
            level = random.randint(newSuitType, newSuitType+7)
            if level > newSuitType+7:
                level = newSuitType+7
            elif level < 7:
                level = 7
            suit = self.__genSuitObject(self.zoneId, newSuitType, 's', level, 0)
            reserveSuits.append((suit, 100))

        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles

    def genSuits(self):
        suitHandles = []
        for floor in xrange(len(self.suitInfos)):
            floorSuitHandles = self.genFloorSuits(floor)
            suitHandles.append(floorSuitHandles)

        return suitHandles
