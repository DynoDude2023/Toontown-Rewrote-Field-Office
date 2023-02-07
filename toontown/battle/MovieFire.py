from panda3d.core import *
from direct.interval.IntervalGlobal import *
from BattleBase import *
from BattleProps import *
from BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from direct.directnotify import DirectNotifyGlobal
from libotp import *
import random
import MovieCamera
import MovieUtil
from MovieUtil import calcAvgSuitPos
notify = DirectNotifyGlobal.directNotify.newCategory('MovieThrow')
hitSoundFiles = ('AA_tart_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_wholepie_only.ogg', 'AA_wholepie_only.ogg')
tPieLeavesHand = 2.7
tPieHitsSuit = 3.0
tSuitDodges = 2.45
ratioMissToHit = 1.5
tPieShrink = 0.7
pieFlyTaskName = 'MovieThrow-pieFly'

def addHit(dict, suitId, hitCount):
    if suitId in dict:
        dict[suitId] += hitCount
    else:
        dict[suitId] = hitCount


def doFires(fires):
    if len(fires) == 0:
        return (None, None)

    suitFiresDict = {}
    for fire in fires:
        suitId = fire['target']['suit'].doId
        if suitId in suitFiresDict:
            suitFiresDict[suitId].append(fire)
        else:
            suitFiresDict[suitId] = [fire]

    suitFires = suitFiresDict.values()
    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0
    suitFires.sort(compFunc)

    totalHitDict = {}
    singleHitDict = {}
    groupHitDict = {}

    for fire in fires:
        suitId = fire['target']['suit'].doId
        if 1:
            if fire['target']['hp'] > 0:
                addHit(singleHitDict, suitId, 1)
                addHit(totalHitDict, suitId, 1)
            else:
                addHit(singleHitDict, suitId, 0)
                addHit(totalHitDict, suitId, 0)

    notify.debug('singleHitDict = %s' % singleHitDict)
    notify.debug('groupHitDict = %s' % groupHitDict)
    notify.debug('totalHitDict = %s' % totalHitDict)

    delay = 0.0
    mtrack = Parallel()
    firedTargets = []
    for sf in suitFires:
        if len(sf) > 0:
            ival = __doSuitFires(sf)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = delay + TOON_FIRE_SUIT_DELAY

    retTrack = Sequence()
    retTrack.append(mtrack)
    camDuration = retTrack.getDuration()
    camTrack = MovieCamera.chooseFireShot(fires, suitFiresDict, camDuration)
    return (retTrack, camTrack)

def __doSuitFires(fires):
    toonTracks = Parallel()
    delay = 0.0
    hitCount = 0
    for fire in fires:
        if fire['target']['hp'] > 0:
            hitCount += 1
        else:
            break

    suitList = []
    for fire in fires:
        if fire['target']['suit'] not in suitList:
            suitList.append(fire['target']['suit'])

    for fire in fires:
        showSuitCannon = 1
        if fire['target']['suit'] not in suitList:
            showSuitCannon = 0
        else:
            suitList.remove(fire['target']['suit'])
        tracks = __throwPie(fire, delay, hitCount, showSuitCannon)
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay = delay + TOON_THROW_DELAY

    return toonTracks


def __showProp(prop, parent, pos):
    prop.reparentTo(parent)
    prop.setPos(pos)


def __animProp(props, propName, propType):
    if 'actor' == propType:
        for prop in props:
            prop.play(propName)

    elif 'model' == propType:
        pass
    else:
        notify.error('No such propType as: %s' % propType)


def __billboardProp(prop):
    scale = prop.getScale()
    prop.setBillboardPointWorld()
    prop.setScale(scale)


def __suitMissPoint(suit, other = render):
    pnt = suit.getPos(other)
    pnt.setZ(pnt[2] + suit.getHeight() * 1.3)
    return pnt


def __propPreflight(props, suit, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    props[1].reparentTo(hidden)
    for ci in xrange(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
    prop.lookAt(targetPnt)


def __propPreflightGroup(props, suits, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    props[1].reparentTo(hidden)
    for ci in xrange(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    avgTargetPt = Point3(0, 0, 0)
    for suit in suits:
        avgTargetPt += MovieUtil.avatarFacePoint(suit, other=battle)

    avgTargetPt /= len(suits)
    prop.lookAt(avgTargetPt)


def __piePreMiss(missDict, pie, suitPoint, other = render):
    missDict['pie'] = pie
    missDict['startScale'] = pie.getScale()
    missDict['startPos'] = pie.getPos(other)
    v = Vec3(suitPoint - missDict['startPos'])
    endPos = missDict['startPos'] + v * ratioMissToHit
    missDict['endPos'] = endPos


def __pieMissLerpCallback(t, missDict):
    pie = missDict['pie']
    newPos = missDict['startPos'] * (1.0 - t) + missDict['endPos'] * t
    if t < tPieShrink:
        tScale = 0.0001
    else:
        tScale = (t - tPieShrink) / (1.0 - tPieShrink)
    newScale = missDict['startScale'] * max(1.0 - tScale, 0.01)
    pie.setPos(newPos)
    pie.setScale(newScale)


def __piePreMissGroup(missDict, pies, suitPoint, other = render):
    missDict['pies'] = pies
    missDict['startScale'] = pies[0].getScale()
    missDict['startPos'] = pies[0].getPos(other)
    v = Vec3(suitPoint - missDict['startPos'])
    endPos = missDict['startPos'] + v * ratioMissToHit
    missDict['endPos'] = endPos
    notify.debug('startPos=%s' % missDict['startPos'])
    notify.debug('v=%s' % v)
    notify.debug('endPos=%s' % missDict['endPos'])


def __pieMissGroupLerpCallback(t, missDict):
    pies = missDict['pies']
    newPos = missDict['startPos'] * (1.0 - t) + missDict['endPos'] * t
    if t < tPieShrink:
        tScale = 0.0001
    else:
        tScale = (t - tPieShrink) / (1.0 - tPieShrink)
    newScale = missDict['startScale'] * max(1.0 - tScale, 0.01)
    for pie in pies:
        pie.setPos(newPos)
        pie.setScale(newScale)


def __getSoundTrackStart(level, hitSuit, node = None):
    remoteSound = globalBattleSoundCache.getSound('AA_remote_control.ogg')
    throwTrack = Sequence(SoundInterval(remoteSound, node=node))
    return throwTrack

def __getSoundTrackEnd(level, hitSuit, node = None):
    remoteHitSound = globalBattleSoundCache.getSound('SA_remote_control.ogg')
    throwTrack = Sequence(SoundInterval(remoteHitSound, node=node))
    return throwTrack

def __throwPie(throw, delay, hitCount, showCannon = 1):
    toon = throw['toon']
    hpbonus = throw['hpbonus']
    target = throw['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    sidestep = throw['sidestep']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    level = throw['level']
    battle = throw['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    notify.debug('toon: %s throws tart at suit: %d for hp: %d died: %d' % (toon.getName(),
     suit.doId,
     hp,
     died))
    pieName = pieNames[0]
    hitSuit = hp > 0
    button = globalPropPool.getProp('ttr_r_prp_bat_remote')

    buttons = [button]
    hands = toon.getRightHands()
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, battle, suitPos)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    soundTrack = __getSoundTrackStart(level, hitSuit, toon)
    soundTrack2 = __getSoundTrackEnd(level, hitSuit, toon)

    taunts = ['At your command.',
              'Reprogramming...',
              'Deleting COGS.EXE...']
    taunt = random.choice(taunts)

    buttonShow = Func(MovieUtil.showProps, buttons, hands)
    buttonScaleUp = LerpScaleInterval(button, 1.0, button.getScale(), startScale=Point3(0.01, 0.01, 0.01))
    buttonScaleDown = LerpScaleInterval(button, 1.0, Point3(0.01, 0.01, 0.01), startScale=button.getScale())
    buttonHide = Func(MovieUtil.removeProps, buttons)
    animAndSound = Parallel(soundTrack2, ActorInterval(suit, 'seizecontrol'))
    suitResponseTrack = Sequence(Wait(3), animAndSound, Func(suit.loop, 'controlidle'), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), buttonScaleDown, buttonHide)
    animAndSoundTrack = Parallel(Func(suit.loop, 'speak'), buttonShow, soundTrack, buttonScaleUp, ActorInterval(toon, 'remoteAttack'))
    movie = Parallel(animAndSoundTrack, suitResponseTrack)
    movie.append(Func(toon.loop, 'neutral'))
    movie.append(Func(toon.setHpr, battle, origHpr))

    return movie
