from libotp import *
from direct.showbase.DirectObject import DirectObject
from toontown.battle.movies.RewardPanel import *
from toontown.battle.movies.BattleSounds import *
import MovieCamera
from direct.directnotify import DirectNotifyGlobal
import types
notify = DirectNotifyGlobal.directNotify.newCategory('MovieToonVictory')

def __findToonReward(rewards, toon):
    for r in rewards:
        if r['toon'] == toon:
            return r

    return None


class ToonVictorySkipper(DirectObject):

    def __init__(self, numToons, noSkip):
        self._numToons = numToons
        self._noSkip = noSkip
        self._startTimes = {}
        self._intervals = []
        self._battle = None
        return

    def destroy(self):
        self._intervals = None
        return

    def getSetupFunc(self, index):
        return Func(self._setupSkipListen, index)

    def getTeardownFunc(self, index):
        return Func(self._teardownSkipListen, index)

    def setBattle(self, battle):
        self._battle = battle

    def setStartTime(self, index, startT):
        self._startTimes[index] = startT

    def setIvals(self, intervals, timeOffset = 0.0):
        for index in self._startTimes:
            self._startTimes[index] += timeOffset

        self._intervals = intervals

    def _setupSkipListen(self, index):
        if not self._noSkip:
            func = Functor(self._skipToon, index)
            self.accept('escape', func)
            self.accept(RewardPanel.SkipBattleMovieEvent, func)

    def _teardownSkipListen(self, index):
        if not self._noSkip:
            self.ignore('escape')
            self.ignore(RewardPanel.SkipBattleMovieEvent)

    def _skipToon(self, index):
        nextIndex = index + 1
        if nextIndex >= self._numToons:
            for interval in self._intervals:
                interval.finish()

            if self._battle:
                self._battle.setSkippingRewardMovie()
        elif nextIndex in self._startTimes:
            for interval in self._intervals:
                interval.setT(self._startTimes[nextIndex])


def doToonVictory(localToonActive, toons, rewardToonIds, rewardDicts, deathList, rpanel, allowGroupShot=1,
                  helpfulToonsList=[], noSkip=False):
    track = Sequence()
    if localToonActive == 1:
        track.append(Func(rpanel.show))
        track.append(Func(NametagGlobals.setOnscreenChatForced, 1))
    camTrack = Sequence()
    endTrack = Sequence()
    danceSound = globalBattleSoundCache.getSound('ENC_Win.ogg')
    toonList = []
    countToons = 0
    for toon in toons:
        if isinstance(toon, types.IntType):
            toon = base.cr.doId2do.get(toon)
        if toon:
            toonList.append(toon)
        countToons += 1

    toonId2toon = {}
    for toon in toonList:
        toonId2toon[toon.doId] = toon

    rewardToonList = []
    for rewardToonId in rewardToonIds:
        rewardToonList.append(toonId2toon.get(rewardToonId))

    skipper = ToonVictorySkipper(len(toonList), noSkip)
    lastListenIndex = 0
    track.append(skipper.getSetupFunc(lastListenIndex))
    for tIndex in xrange(len(toonList)):
        toon = toonList[tIndex]
        rdict = __findToonReward(rewardDicts, toon)
        if rdict:
            expTrack = rpanel.getExpTrack(toon, rdict['origExp'], rdict['earnedExp'], deathList, rdict['origQuests'],
                                          rdict['items'], rdict['missedItems'], rdict['origMerits'], rdict['merits'],
                                          rdict['parts'], rewardToonList, helpfulToonsList, noSkip=noSkip)
            if expTrack:
                skipper.setStartTime(tIndex, track.getDuration())
                track.append(skipper.getTeardownFunc(lastListenIndex))
                lastListenIndex = tIndex
                track.append(skipper.getSetupFunc(lastListenIndex))
                track.append(expTrack)
                camDuration = expTrack.getDuration()
                camExpTrack = MovieCamera.chooseRewardShot(toon, camDuration)
                camTrack.append(MovieCamera.chooseRewardShot(toon, camDuration, allowGroupShot=allowGroupShot))

    track.append(skipper.getTeardownFunc(lastListenIndex))
    track.append(Func(skipper.destroy))
    if localToonActive == 1:
        track.append(Func(rpanel.hide))
        track.append(Func(NametagGlobals.setOnscreenChatForced, 0))
    track.append(endTrack)
    trackdur = track.getDuration()
    soundTrack = SoundInterval(danceSound, duration=trackdur, loop=1)
    mtrack = Parallel(track, soundTrack)
    skipper.setIvals((mtrack, camTrack))
    return (mtrack, camTrack, skipper)
