from BattleBase import *
import copy
import random

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.directnotify import DirectNotifyGlobal
from panda3d.core import Point4

from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
notify = DirectNotifyGlobal.directNotify.newCategory('SuitBattleGlobals')
debugAttackSequence = {}

def pickFromFreqList(freqList):
    randNum = random.randint(0, 99)
    count = 0
    index = 0
    level = None
    for f in freqList:
        count = count + f
        if randNum < count:
            level = index
            break
        index = index + 1

    return level


def getActualFromRelativeLevel(name, relLevel):
    data = SuitAttributes[name]
    actualLevel = data['level'] + relLevel
    return actualLevel


def getSuitDataFromName(name):
    return SuitAttributes[name]


def getSuitData(name, level=-1):
    data = SuitAttributes[name]
    if level == -1:
        level = pickFromFreqList(data['freq'])
    suitDict = {'level': getActualFromRelativeLevel(name, level),
                'hp': data['hp'][level],
                'def': data['def'][level]}
    attacks = data['attacks']
    attackList = []
    for attack in attacks:
        adict = {}
        name = attack[0]
        adict['name'] = name
        adict['animName'] = SuitAttacks[name][0]
        adict['hp'] = attack[1][level]
        adict['acc'] = attack[2][level]
        adict['freq'] = attack[3][level]
        adict['group'] = SuitAttacks[name][1]
        attackList.append(adict)

    suitDict['attacks'] = attackList
    return suitDict


def pickSuitAttack(attacks, suitLevel):
    attackNum = None
    randNum = random.randint(0, 99)
    notify.debug('pickSuitAttack: rolled %d' % randNum)
    count = 0
    index = 0
    total = 0
    for attack in attacks:
        total = total + attack[3][suitLevel]

    for attack in attacks:
        count = count + attack[3][suitLevel]
        if randNum < count:
            attackNum = index
            notify.debug('picking attack %d' % attackNum)
            break
        index = index + 1

    configAttackName = simbase.config.GetString('attack-type', 'random')
    if configAttackName == 'random':
        return attackNum
    elif configAttackName == 'sequence':
        for i in xrange(len(attacks)):
            if attacks[i] not in debugAttackSequence:
                debugAttackSequence[attacks[i]] = 1
                return i

        return attackNum
    else:
        for i in xrange(len(attacks)):
            if attacks[i][0] == configAttackName:
                return i

        return attackNum


def getSuitAttack(suitName, suitLevel, attackNum=-1):
    attackChoices = SuitAttributes[suitName]['attacks']
    if attackNum == -1:
        notify.debug('getSuitAttack: picking attacking for %s' % suitName)
        attackNum = pickSuitAttack(attackChoices, suitLevel)
    attack = attackChoices[attackNum]
    name = attack[0]
    adict = {'suitName': suitName,
             'name': name,
             'id': SuitAttacks.keys().index(name),
             'animName': SuitAttacks[name][0],
             'hp': attack[1][suitLevel],
             'acc': attack[2][suitLevel],
             'freq': attack[3][suitLevel],
             'group': SuitAttacks[name][1]}
    return adict

def getSuitAttack(suitName, suitLevel, attackNum = -1):
    attackChoices = SuitAttributes[suitName]['attacks']
    if attackNum == -1:
        notify.debug('getSuitAttack: picking attacking for %s' % suitName)
        attackNum = pickSuitAttack(attackChoices, suitLevel)
    attack = attackChoices[attackNum]
    adict = {}
    adict['suitName'] = suitName
    name = attack[0]
    adict['name'] = name
    adict['id'] = SuitAttacks.keys().index(name)
    adict['animName'] = SuitAttacks[name][0]
    adict['hp'] = attack[1][suitLevel]
    adict['acc'] = attack[2][suitLevel]
    adict['freq'] = attack[3][suitLevel]
    adict['group'] = SuitAttacks[name][1]
    return adict

MAX_SUIT_CAPACITY = 4
SUIT_CAPACITY = 4

# Formatted by Jake S. - You're welcome!
SuitAttributes = {'f': {'name': TTLocalizer.SuitFlunky, # cog name
       'singularname': TTLocalizer.SuitFlunkyS, # cogs singular name, for tasks
       'pluralname': TTLocalizer.SuitFlunkyP, # cogs plural name, for tasks
       'level': 0, # level the cog starts at (level - 1)
       'hp':(6,12,20,30,42), # cogs hp (more numbers, more levels)
       'def':(2,5,10,12,15), # cogs defence (more numbers, more levels)
       'freq':(50,30,10,5,5), # cogs level frequency
       'acc':(35,40,45,50,55), # cogs accuracy (more numbers, more levels)
       'attacks':
                (('PoundKey',
                    (2,2,3,4,6), # attack damage
                    (75,75,80,80,90), # attack accuracy
                    (30,35,40,45,50)), # move frequency (all move frequency of each attack must add up to 100, for example 30,10,60 from level 1 of each attack)
                ('Shred',
                    (3,4,5,6,7),
                    (50,55,60,65,70),
                    (10,15,20,25,30)),
                ('ClipOnTie',
                    (1,1,2,2,3),
                    (75,80,85,90,95),
                    (60,50,40,30,20)))},
 'p': {'name': TTLocalizer.SuitPencilPusher,
       'singularname': TTLocalizer.SuitPencilPusherS,
       'pluralname': TTLocalizer.SuitPencilPusherP,
       'level': 1,
       'hp':(12,20,30,42,56),
       'def':(5,10,15,20,25),
       'freq':(50,30,10,5,5),
       'acc':(45,50,55,60,65),
       'attacks':
                (('FountainPen',
                    (2,3,4,6,9),
                    (75,75,75,75,75),
                    (20,20,20,20,20)),
                ('RubOut',
                    (4,5,6,8,12),
                    (75,75,75,75,75),
                    (20,20,20,20,20)),
                ('FingerWag',
                    (1,2,2,3,4),
                    (75,75,75,75,75),
                    (35,30,25,20,15)),
                ('WriteOff',
                    (4,6,8,10,12),
                    (75,75,75,75,75),
                    (5,10,15,20,25)),
                ('FillWithLead',
                    (3,4,5,6,7),
                    (75,75,75,75,75),
                    (20,20,20,20,20)))},
 'ym': {'name': TTLocalizer.SuitYesman,
        'singularname': TTLocalizer.SuitYesmanS,
        'pluralname': TTLocalizer.SuitYesmanP,
        'level': 2,
        'hp':(20,30,42,56,72),
        'def':(10,15,20,25,30),
        'freq':(50,30,10,5,5),
        'acc':(65,70,75,80,85),
        'attacks':
                (('RubberStamp',
                    (2,2,3,3,4),
                    (75,75,75,75,75),
                    (35,35,35,35,35)),
                ('RazzleDazzle',
                    (1,1,1,1,1),
                    (50,50,50,50,50),
                    (25,20,15,10,5)),
                ('Synergy',
                    (4,5,6,7,8),
                    (50,60,70,80,90),
                    (5,10,15,20,25)),
                ('TeeOff',
                    (3,3,4,4,5),
                    (50,60,70,80,90),
                    (35,35,35,35,35)))},
 'mm': {'name': TTLocalizer.SuitMicromanager,
        'singularname': TTLocalizer.SuitMicromanagerS,
        'pluralname': TTLocalizer.SuitMicromanagerP,
        'level': 3,
        'hp':(30,42,56,72,90),
        'def':(15,20,25,30,35),
        'freq':(50,30,10,5,5),
        'acc':(70,75,80,82,85),
        'attacks':
                (('Demotion',
                    (6,8,12,15,18),
                    (50,60,70,80,90),
                    (30,30,30,30,30)),
                ('FingerWag',
                    (4,6,9,12,15),
                    (50,60,70,80,90),
                    (10,10,10,10,10)),
                ('FountainPen',
                    (3,4,6,8,10),
                    (50,60,70,80,90),
                    (15,15,15,15,15)),
                ('BrainStorm',
                    (4,6,9,12,15),
                    (5,5,5,5,5),
                    (25,25,25,25,25)),
                ('BuzzWord',
                    (4,6,9,12,15),
                    (50,60,70,80,90),
                    (20,20,20,20,20)))},
 'ds': {'name': TTLocalizer.SuitDownsizer,
        'singularname': TTLocalizer.SuitDownsizerS,
        'pluralname': TTLocalizer.SuitDownsizerP,
        'level': 4,
        'hp':(42,56,72,90,110),
        'def':(20,25,30,35,40),
        'freq':(50,30,10,5,5),
        'acc':(35,40,45,50,55),
        'attacks':
                (('Canned',
                    (5,6,8,10,12),
                    (60,75,80,85,90),
                    (25,25,25,25,25)),
                ('Downsize',
                    (8,9,11,13,15),
                    (50,65,70,75,80),
                    (35,35,35,35,35)),
                ('PinkSlip',
                    (4,5,6,7,8),
                    (60,65,75,80,85),
                    (25,25,25,25,25)),
                ('Sacked',
                    (5,6,7,8,9),
                    (50,50,50,50,50),
                    (15,15,15,15,15)))},
 'hh': {'name': TTLocalizer.SuitHeadHunter,
        'singularname': TTLocalizer.SuitHeadHunterS,
        'pluralname': TTLocalizer.SuitHeadHunterP,
        'level': 5,
        'hp':(56,72,90,110,132),
        'def':(25,30,35,40,45),
        'freq':(50,30,10,5,5),
        'acc':(35,40,45,50,55),
        'attacks':
                (('FountainPen',
                    (5,6,8,10,12),
                    (60,75,80,85,90),
                    (15,15,15,15,15)),
                ('GlowerPower',
                    (7,8,10,12,13),
                    (50,60,70,80,90),
                    (20,20,20,20,20)),
                ('HalfWindsor',
                    (8,10,12,14,16),
                    (60,65,70,75,80),
                    (20,20,20,20,20)),
                ('HeadShrink',
                    (10,12,15,18,21),
                    (65,75,80,85,95),
                    (35,35,35,35,35)),
                ('Rolodex',
                    (6,7,8,9,10),
                    (60,65,70,75,80),
                    (10,10,10,10,10)))},
 'cr': {'name': TTLocalizer.SuitCorporateRaider,
        'singularname': TTLocalizer.SuitCorporateRaiderS,
        'pluralname': TTLocalizer.SuitCorporateRaiderP,
        'level': 6,
        'hp':(72,90,110,132,156),
        'def':(30,35,40,45,50),
        'freq':(50,30,10,5,5),
        'acc':(35,40,45,50,55),
        'attacks':
            (('Canned',
                (6,7,8,9,10),
                (60,75,80,85,90),
                (20,20,20,20,20)),
            ('EvilEye',
                (12,15,18,21,24),
                (60,70,75,80,90),
                (35,35,35,35,35)),
            ('PlayHardball',
                (7,8,12,15,16),
                (60,65,70,75,80),
                (30,30,30,30,30)),
            ('PowerTie',
                (10,12,14,16,18),
                (65,75,80,85,95),
                (15,15,15,15,15)))},
 'tbc': {'name': TTLocalizer.SuitTheBigCheese,
         'singularname': TTLocalizer.SuitTheBigCheeseS,
         'pluralname': TTLocalizer.SuitTheBigCheeseP,
         'level': 7,
         'hp':(90,110,132,156,198,224,254,286,320,356,394,434,476,500),
         'def':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
         'freq':(50,30,10,5,5),
         'acc':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
         'attacks':
                (('CigarSmoke',
                    (10,12,15,18,20,22,23,24,25,26,27,28,29,30),
                    (55,65,75,85,95,95,95,95,95,95,95,95,95,95),
                    (20,20,20,20,20,20,20,20,20,20,20,20,20,20)),
                ('FloodTheMarket',
                    (14,16,18,20,22,23,23,24,25,26,27,28,29,30),
                    (70,75,85,90,95,95,95,95,95,95,95,95,95,95),
                    (10,10,10,10,10,10,10,10,10,10,10,10,10,10)),
                ('SongAndDance',
                    (14,15,17,19,20,21,22,23,24,25,26,27,28,29),
                    (60,65,70,75,80,85,90,90,90,90,90,90,90,90),
                    (20,20,20,20,20,20,20,20,20,20,20,20,20,20)),
                ('TeeOff',
                    (8,11,14,17,20,21,21,22,22,23,23,24,24,25),
                    (55,65,70,75,80,85,90,90,90,90,90,90,90,90),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)))},
 'sbc': {'name': TTLocalizer.SuitTheBigCheese,
         'singularname': TTLocalizer.SuitTheBigCheeseS,
         'pluralname': TTLocalizer.SuitTheBigCheeseP,
         'level': 7,
         'hp':(90,110,132,156,198,224,254,286,320,356,394,434,476,500),
         'def':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
         'freq':(50,30,10,5,5),
         'acc':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
         'attacks':
                (('CigarSmoke',
                    (10,12,15,18,20,22,23,24,25,26,27,28,29,30),
                    (55,65,75,85,95,95,95,95,95,95,95,95,95,95),
                    (20,20,20,20,20,20,20,20,20,20,20,20,20,20)),
                ('FloodTheMarket',
                    (14,16,18,20,22,23,23,24,25,26,27,28,29,30),
                    (70,75,85,90,95,95,95,95,95,95,95,95,95,95),
                    (10,10,10,10,10,10,10,10,10,10,10,10,10,10)),
                ('SongAndDance',
                    (14,15,17,19,20,21,22,23,24,25,26,27,28,29),
                    (60,65,70,75,80,85,90,90,90,90,90,90,90,90),
                    (20,20,20,20,20,20,20,20,20,20,20,20,20,20)),
                ('TeeOff',
                    (8,11,14,17,20,21,21,22,22,23,23,24,24,25),
                    (55,65,70,75,80,85,90,90,90,90,90,90,90,90),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)))},
 'cc': {'name': TTLocalizer.SuitColdCaller,
        'singularname': TTLocalizer.SuitColdCallerS,
        'pluralname': TTLocalizer.SuitColdCallerP,
        'level': 0,
        'hp':(6,12,20,30,42,56,72,90),
        'def':(2,5,10,12,15,17,19,21),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,55,55,55),
        'attacks':
                (('FreezeAssets',
                    (1,1,1,1,1,4,6,8),
                    (90,90,90,90,90,90,90,90),
                    (5,10,15,20,25,25,25,25)),
                ('PoundKey',
                    (2,2,3,4,5,6,7,8),
                    (75,80,85,90,95,95,95,95),
                    (25,25,25,25,25,25,25,25)),
                ('DoubleTalk',
                    (2,3,4,6,8,10,12,14),
                    (50,55,60,65,70,70,70,70),
                    (25,25,25,25,25,25,25,25)),
                ('HotAir',
                    (3,4,6,8,10,12,14,16),
                    (50,50,50,50,50,50,50,50),
                    (45,40,35,30,25,25,25,25)),
                ('BurnOut',
                    (3,4,6,8,10,12,14,16),
                    (50,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)))},
 'bo': {'name': TTLocalizer.SuitColdCaller,
        'singularname': TTLocalizer.SuitColdCallerS,
        'pluralname': TTLocalizer.SuitColdCallerP,
        'level': 0,
        'hp':(3000,12,20,30,42,56,72,90),
        'def':(2,5,10,12,15,17,19,21),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,55,55,55),
        'attacks':
                (('BurnOut',
                    (30,1,1,1,1,4,6,8),
                    (90,90,90,90,90,90,90,90),
                    (100,10,15,20,25,25,25,25)),
                ('OffenseMode',
                    (0,4,6,8,10,12,14,16),
                    (0,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)),
                ('Promotion',
                    (0,4,6,8,10,12,14,16),
                    (0,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)))},
 'tm': {'name': TTLocalizer.SuitTelemarketer,
        'singularname': TTLocalizer.SuitTelemarketerS,
        'pluralname': TTLocalizer.SuitTelemarketerP,
        'level': 1,
        'hp':(12,20,30,42,56,72,90,110),
        'def':(5,10,15,20,25,30,35,40),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(45,50,55,60,65,70,75,80),
        'attacks':
                (('ClipOnTie',
                    (2,2,3,3,4,6,8,12),
                    (75,75,75,75,75,75,75,75),
                    (15,15,15,15,15,15,15,15)),
                ('PickPocket',
                    (1,1,1,1,1,1,2,2),
                    (75,75,75,75,75),
                    (15,15,15,15,15,15,15,15)),
                ('Rolodex',
                    (4,6,7,9,12,15,18,22),
                    (50,50,50,50,50,50,50,50),
                    (30,30,30,30,30,30,30,30)),
                ('DoubleTalk',
                    (4,6,7,9,12,15,18,22),
                    (75,80,85,90,95,95,95,95),
                    (40,40,40,40,40,40,40,40)),
                ('BurnOut',
                    (3,4,6,8,10,12,14,16),
                    (50,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)))},
 'nd': {'name': TTLocalizer.SuitNameDropper,
        'singularname': TTLocalizer.SuitNameDropperS,
        'pluralname': TTLocalizer.SuitNameDropperP,
        'level': 2,
        'hp':(20,30,42,56,72,90,110,132),
        'def':(10,15,20,25,30,35,40,45),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(65,70,75,80,85,90,95,100),
        'attacks':
                (('RazzleDazzle',
                    (4,5,6,9,12,15,18,21),
                    (75,80,85,90,95,95,95,95),
                    (30,30,30,30,30,30,30,30)),
                ('Rolodex',
                    (5,6,7,10,14,18,21,25),
                    (95,95,95,95,95,95,95,95),
                    (40,40,40,40,40,40,40,40)),
                ('Synergy',
                    (3,4,6,9,12,15,18,21),
                    (50,50,50,50,50,50,50,50),
                    (15,15,15,15,15,15,15,15)),
                ('PickPocket',
                    (2,2,2,2,2,3,4,6),
                    (95,95,95,95,95,95,95,95),
                    (15,15,15,15,15,15,15,15)),
                ('BurnOut',
                    (3,4,6,8,10,12,14,16),
                    (50,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)))},
 'gh': {'name': TTLocalizer.SuitGladHander,
        'singularname': TTLocalizer.SuitGladHanderS,
        'pluralname': TTLocalizer.SuitGladHanderP,
        'level': 3,
        'hp':(30,42,56,72,90,110,132,156),
        'def':(15,20,25,30,35,40,45,50),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(70,75,80,82,85,90,95,100),
        'attacks':
                (('RubberStamp',
                    (4,3,3,2,1,1,1,1),
                    (90,70,50,30,10,10,10,10),
                    (40,30,20,10,5,5,5,5)),
                ('FountainPen',
                    (3,3,2,1,1,1,1,1),
                    (70,60,50,40,30,30,30,30),
                    (40,30,20,10,5,5,5,5)),
                ('Filibuster',
                    (4,6,9,12,15,15,15,15),
                    (30,40,50,60,70,70,70,70),
                    (10,20,30,40,45,45,45,45)),
                ('Schmooze',
                    (5,7,11,15,20,20,20,20),
                    (55,65,75,85,95,95,95,95),
                    (10,20,30,40,45,45,45,45)),
                ('SongAndDance',
                    (0,0,0,0,0,0,0,0),
                    (55,65,75,85,95,95,95,95),
                    (0,0,0,0,0,0,0,0)),
                ('BurnOut',
                    (3,4,6,8,10,12,14,16),
                    (50,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)))},
 'ms': {'name': TTLocalizer.SuitMoverShaker,
        'singularname': TTLocalizer.SuitMoverShakerS,
        'pluralname': TTLocalizer.SuitMoverShakerP,
        'level': 4,
        'hp':(42,56,72,90,110,132,156,198),
        'def':(20,25,30,35,40,40,45,50),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('BrainStorm',
                    (5,6,8,10,12,14,16,18),
                    (60,75,80,85,90,95,100,105),
                    (15,15,15,15,15,15,15,15)),
                ('HalfWindsor',
                    (6,9,11,13,16,18,20,22),
                    (50,65,70,75,80,85,90,95),
                    (20,20,20,20,20,20,20,20)),
                ('Quake',
                    (9,12,15,18,21,24,27,30),
                    (60,65,75,80,85,90,95,100),
                    (20,20,20,20,20,20,20,20)),
                ('Shake',
                    (6,8,10,12,14,16,18,20),
                    (70,75,80,85,90,95,100,105),
                    (25,25,25,25,25,25,25,25)),
                ('Tremor',
                    (5,6,7,8,9,10,11,12),
                    (50,50,50,50,50,50,50,50),
                    (20,20,20,20,20,20,20,20)),
                ('BurnOut',
                    (3,4,6,8,10,12,14,16),
                    (50,50,50,50,50,50,50,50),
                    (0,0,0,0,0,0,0,0)))},
 'tf': {'name': TTLocalizer.SuitTwoFace,
        'singularname': TTLocalizer.SuitTwoFaceS,
        'pluralname': TTLocalizer.SuitTwoFaceP,
        'level': 5,
        'hp':(56,72,90,110,132,156,198,224),
        'def':(25,30,35,40,45,45,50,55),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('EvilEye',
                    (10,12,14,16,18,20,22,24),
                    (60,75,80,85,90,90,90,90),
                    (30,30,30,30,30,30,30,30)),
                ('HangUp',
                    (7,8,10,12,13,15,16,18),
                    (50,60,70,80,90,90,90,90),
                    (15,15,15,15,15,15,15,15)),
                ('RazzleDazzle',
                    (8,10,12,14,16,18,20,22),
                    (60,65,70,75,80,80,80,80),
                    (30,30,30,30,30,30,30,30)),
                ('RedTape',
                    (6,7,8,9,10,11,12,13),
                    (60,65,75,85,90,90,90,90),
                    (25,25,25,25,25,25,25,25)))},
 'm': {'name': TTLocalizer.SuitTheMingler,
       'singularname': TTLocalizer.SuitTheMinglerS,
       'pluralname': TTLocalizer.SuitTheMinglerP,
       'level': 6,
       'hp':(72,90,110,132,156,198,224,254),
       'def':(30,35,40,45,50,50,55,60),
       'freq':(50,30,10,5,5,5,5,5),
       'acc':(35,40,45,50,55,60,65,70),
       'attacks':
               (('BuzzWord',
                    (10,11,13,15,16,18,20,21),
                    (60,75,80,85,90,90,90,90),
                    (20,20,20,20,20,20,20,20)),
                ('ParadigmShift',
                    (12,15,18,21,24,27,30,33),
                    (60,70,75,80,90,90,90,90),
                    (25,25,25,25,25,25,25,25)),
                ('PowerTrip',
                    (10,13,14,15,18,20,22,25),
                    (60,65,70,75,80,80,80,80),
                    (15,15,15,15,15,15,15,15)),
                ('Schmooze',
                    (7,8,12,15,16,18,20,22),
                    (55,65,75,85,95,95,95,95),
                    (30,30,30,30,30,30,30,30)),
                ('TeeOff',
                    (8,9,10,11,12,13,15,16),
                    (70,75,80,85,95,95,95,95),
                    (10,10,10,10,10,10,10,10)))},
 'hfm': {'name': "Hedge Fund Manager",
       'singularname': TTLocalizer.SuitTheMinglerS,
       'pluralname': TTLocalizer.SuitTheMinglerP,
       'level': 6,
       'hp':(72,90,110,132,156,198,224,254),
       'def':(30,35,40,45,50,50,55,60),
       'freq':(50,30,10,5,5,5,5,5),
       'acc':(35,40,45,50,55,60,65,70),
       'attacks':
               (('AdvancedSynergy',
                    (10,11,13,15,16,18,20,21),
                    (60,75,80,85,90,90,90,90),
                    (20,20,20,20,20,20,20,20)),
                ('AdvancedSynergy',
                    (12,15,18,24,27,30,33,36),
                    (60,70,75,80,90,90,90,90),
                    (25,25,25,25,25,25,25,25)),
                ('PowerTrip',
                    (10,13,14,15,18,24,27,32),
                    (60,65,70,75,80,80,80,80),
                    (15,15,15,15,15,15,15,15)),
                ('AdvancedSynergy',
                    (7,8,12,15,16,18,30,34),
                    (55,65,75,85,95,95,95,95),
                    (30,30,30,30,30,30,30,30)),
                ('TeeOff',
                    (8,9,10,11,12,13,15,16),
                    (70,75,80,85,95,95,95,95),
                    (10,10,10,10,10,10,10,10)))},
 'mh': {'name': TTLocalizer.SuitMrHollywood,
        'singularname': TTLocalizer.SuitMrHollywoodS,
        'pluralname': TTLocalizer.SuitMrHollywoodP,
        'level': 7,
        'hp':(90,110,132,156,198,224,254,286,320,356,394,434,476,500),
        'def':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
        'freq':(50,30,10,5,5),
        'acc':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
        'attacks':
                (('PowerTrip',
                    (10,12,15,18,20,22,24,26,28,30,32,34,36,38),
                    (55,65,75,85,95,95,95,95,95,95,95,95,95,95),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)),
                ('RazzleDazzle',
                    (8,11,14,17,20,22,24,26,28,30,32,34,36,38),
                    (70,75,85,90,95,95,95,95,95,95,95,95,95,95),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)))},
 'sc': {'name': TTLocalizer.SuitShortChange,
        'singularname': TTLocalizer.SuitShortChangeS,
        'pluralname': TTLocalizer.SuitShortChangeP,
        'level': 0,
        'hp':(6,12,20,30,42,56,72,90),
        'def':(2,5,10,12,15,18,20,22),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('Watercooler',
                    (2,2,3,4,6,8,10,12),
                    (50,50,50,50,50,50,50,50),
                    (20,20,20,20,20,20,20,20)),
                ('BounceCheck',
                    (3,5,7,9,11,13,15,17),
                    (75,80,85,90,95,95,95,95),
                    (15,15,15,15,15,15,15,15)),
                ('ClipOnTie',
                    (1,1,2,2,3,3,4,5),
                    (50,50,50,50,50,50,50,50),
                    (25,25,25,25,25,25,25,25)),
                ('PickPocket',
                    (2,2,3,4,6,8,10,12),
                    (95,95,95,95,95,95,95,95),
                    (40,40,40,40,40,40,40,40)))},
 'pp': {'name': TTLocalizer.SuitPennyPincher,
        'singularname': TTLocalizer.SuitPennyPincherS,
        'pluralname': TTLocalizer.SuitPennyPincherP,
        'level': 1,
        'hp':(12,20,30,42,56,72,90,110),
        'def':(5,10,15,20,25,30,35,40),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(45,50,55,60,65,70,75,80),
        'attacks':
                (('BounceCheck',
                    (4,5,6,8,12,15,18,20),
                    (75,75,75,75,75,75,75,75),
                    (45,45,45,45,45,45,45,45)),
                ('FreezeAssets',
                    (2,3,4,6,9,12,15,18),
                    (75,75,75,75,75,75,75,75),
                    (20,20,20,20,20,20,20,20)),
                ('FingerWag',
                    (1,2,3,4,6,9,12,15),
                    (50,50,50,50,50,50,50,50),
                    (35,35,35,35,35,35,35,35)))},
 'tw': {'name': TTLocalizer.SuitTightwad,
        'singularname': TTLocalizer.SuitTightwadS,
        'pluralname': TTLocalizer.SuitTightwadP,
        'level': 2,
        'hp':(20,30,42,56,72,90,110,132),
        'def':(10,15,20,25,30,35,40,45),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(65,70,75,80,85,90,95,100),
        'attacks':
                (('Fired',
                    (3,4,5,5,6,7,8,9),
                    (75,75,75,75,75,75,75,75),
                    (75,5,5,5,5,5,5,5)),
                ('GlowerPower',
                    (3,4,6,9,12,15,18,21),
                    (95,95,95,95,95,95,95,95),
                    (10,15,20,25,30,35,40,45)),
                ('FingerWag',
                    (3,3,4,4,5,6,7,8),
                    (75,75,75,75,75,75,75,75),
                    (5,70,5,5,5,5,5,5)),
                ('FreezeAssets',
                    (3,4,6,9,12,15,18,21),
                    (75,75,75,75,75,75,75,75),
                    (5,5,65,5,30,30,30,30)),
                ('BounceCheck',
                    (5,6,9,13,18,23,28,33),
                    (75,75,75,75,75,75,75,75),
                    (5,5,5,60,30,30,30,30)))},
 'bc': {'name': TTLocalizer.SuitBeanCounter,
        'singularname': TTLocalizer.SuitBeanCounterS,
        'pluralname': TTLocalizer.SuitBeanCounterP,
        'level': 3,
        'hp':(30,42,56,72,90,110,132,156),
        'def':(15,20,25,30,35,40,45,50),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(70,75,80,82,85,88,90,95),
        'attacks':
                (('Audit',
                    (4,6,9,12,15,18,21,24),
                    (95,95,95,95,95,95,95,95),
                    (20,20,20,20,20,20,20,20)),
                ('Calculate',
                    (4,6,9,12,15,18,21,24),
                    (75,75,75,75,75,75,75,75),
                    (25,25,25,25,25,25,25,25)),
                ('Tabulate',
                    (4,6,9,12,15,18,21,24),
                    (75,75,75,75,75,75,75,75),
                    (25,25,25,25,25,25,25,25)),
                ('WriteOff',
                    (4,6,9,12,15,18,21,24),
                    (95,95,95,95,95,95,95,95),
                    (30,30,30,30,30,30,30,30)))},
 'nc': {'name': TTLocalizer.SuitNumberCruncher,
        'singularname': TTLocalizer.SuitNumberCruncherS,
        'pluralname': TTLocalizer.SuitNumberCruncherP,
        'level': 4,
        'hp':(42,56,72,90,110,132,156,198),
        'def':(20,25,30,35,40,45,50,55),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('Audit',
                    (5,6,8,10,12,14,16,18),
                    (60,75,80,85,90,95,100,105),
                    (15,15,15,15,15,15,15,15)),
                ('Calculate',
                    (6,7,9,11,13,15,18,20),
                    (50,65,70,75,80,85,90,95),
                    (30,30,30,30,30,30,30,30)),
                ('Crunch',
                    (8,9,11,13,15,17,19,21),
                    (60,65,75,80,85,90,95,100),
                    (35,35,35,35,35,35,35,35)),
                ('Tabulate',
                    (5,6,7,8,9,10,11,12),
                    (50,50,50,50,50,50,50,50),
                    (20,20,20,20,20,20,20,20)))},
 'mb': {'name': TTLocalizer.SuitMoneyBags,
        'singularname': TTLocalizer.SuitMoneyBagsS,
        'pluralname': TTLocalizer.SuitMoneyBagsP,
        'level': 5,
        'hp':(56,72,90,110,132,156,198,224),
        'def':(25,30,35,40,45,50,55,60),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('Liquidate',
                    (10,12,14,16,18,20,22,24),
                    (60,75,80,85,90,95,100,105),
                    (30,30,30,30,30,30,30,30)),
                ('MarketCrash',
                    (8,10,12,14,16,18,20,22),
                    (60,65,70,75,80,85,90,95),
                    (45,45,45,45,45,45,45,45)),
                ('PowerTie',
                    (6,7,8,9,10,11,12,13),
                    (60,65,75,85,90,95,100,105),
                    (25,25,25,25,25,25,25,25)))},
 'ls': {'name': TTLocalizer.SuitLoanShark,
        'singularname': TTLocalizer.SuitLoanSharkS,
        'pluralname': TTLocalizer.SuitLoanSharkP,
        'level': 6,
        'hp':(72,90,110,132,156,198,224,254),
        'def':(30,35,40,45,50,55,60,65),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('Bite',
                    (10,11,13,15,16,18,20,22),
                    (60,75,80,85,90,95,100,105),
                    (30,30,30,30,30,30,30,30)),
                ('Chomp',
                    (12,15,18,21,24,27,30,33),
                    (60,70,75,80,90,95,100,105),
                    (35,35,35,35,35,35,35,35)),
                ('PlayHardball',
                    (9,11,12,13,15,16,18,20),
                    (55,65,75,85,95,100,105,110),
                    (20,20,20,20,20,20,20,20)),
                ('WriteOff',
                    (6,8,10,12,14,16,18,20),
                    (70,75,80,85,95,100,105,110),
                    (15,15,15,15,15,15,15,15)))},
 'rb': {'name': TTLocalizer.SuitRobberBaron,
        'singularname': TTLocalizer.SuitRobberBaronS,
        'pluralname': TTLocalizer.SuitRobberBaronP,
        'level': 7,
        'hp':(90,110,132,156,198,224,254,286,320,356,394,434,476,500),
        'def':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
        'freq':(50,30,10,5,5),
        'acc':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
        'attacks':
                (('PowerTrip',
                    (11,14,16,18,21,22,23,24,25,26,27,28,29,30),
                    (60,65,70,75,80,80,80,85,90,90,90,90,90,90),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)),
                ('TeeOff',
                    (10,12,14,16,18,20,22,24,26,27,28,29,30,31),
                    (60,65,75,85,90,90,90,90,95,95,95,95,95,95),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)))},

 'bf': {'name': TTLocalizer.SuitBottomFeeder,
        'singularname': TTLocalizer.SuitBottomFeederS,
        'pluralname': TTLocalizer.SuitBottomFeederP,
        'level': 0,
        'hp':(6,12,20,30,42,56,72,90),
        'def':(2,5,10,12,15,18,20,25),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('RubberStamp',
                    (2,3,4,5,6,7,8,9),
                    (75,80,85,90,95,95,95,95),
                    (20,20,20,20,20,20,20,20)),
                ('Shred',
                    (2,4,6,8,10,12,14,16),
                    (50,55,60,65,70,75,80,85),
                    (20,20,20,20,20,20,20,20)),
                ('Watercooler',
                    (3,4,5,6,7,8,9,10),
                    (95,95,95,95,95,95,95,95),
                    (10,10,10,10,10,10,10,10)),
                ('PickPocket',
                    (1,1,2,2,3,3,4,5),
                    (25,30,35,40,45,50,55,60),
                    (50,50,50,50,50,50,50,50)))},
 'b': {'name': TTLocalizer.SuitBloodsucker,
       'singularname': TTLocalizer.SuitBloodsuckerS,
       'pluralname': TTLocalizer.SuitBloodsuckerP,
       'level': 1,
       'hp':(12,20,30,42,56,72,90,110),
       'def':(5,10,15,20,25,30,35,40),
       'freq':(50,30,10,5,5,5,5,5),
       'acc':(45,50,55,60,65,70,75,80),
       'attacks':
                (('EvictionNotice',
                    (1,2,3,3,4,5,6,7),
                    (75,75,75,75,75,75,75,75),
                    (20,20,20,20,20,20,20,20)),
                ('RedTape',
                    (2,3,4,6,9,12,15,18),
                    (75,75,75,75,75,75,75,75),
                    (20,20,20,20,20,20,20,20)),
                ('Withdrawal',
                    (6,8,10,12,14,16,18,20),
                    (95,95,95,95,95,95,95,95),
                    (10,10,10,10,10,10,10,10)),
                ('Liquidate',
                    (2,3,4,6,9,12,15,18),
                    (50,60,70,80,90,95,95,95),
                    (50,50,50,50,50,50,50,50)))},
 'dt': {'name': TTLocalizer.SuitDoubleTalker,
        'singularname': TTLocalizer.SuitDoubleTalkerS,
        'pluralname': TTLocalizer.SuitDoubleTalkerP,
        'level': 2,
        'hp':(20,30,42,56,72,90,110,132),
        'def':(10,15,20,25,30,35,40,45),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(65,70,75,80,85,90,95,100),
        'attacks':
                (('RubberStamp',
                    (1,1,1,1,1,1,1,1),
                    (50,60,70,80,90,95,95,100),
                    (5,5,5,5,5,5,5,5)),
                ('BounceCheck',
                    (1,1,1,1,1,1,1,1),
                    (50,60,70,80,90,95,95,100),
                    (5,5,5,5,5,5,5,5)),
                ('BuzzWord',
                    (1,2,3,5,6,7,9,12),
                    (50,60,70,80,90,95,95,100),
                    (20,20,20,20,20,20,20,20)),
                ('DoubleTalk',
                    (6,6,9,13,18,23,28,33),
                    (50,60,70,80,90,95,95,100),
                    (25,25,25,25,25,25,25,25)),
                ('Jargon',
                    (3,4,6,9,12,15,18,21),
                    (50,60,70,80,90,95,95,100),
                    (25,25,25,25,25,25,25,25)),
                ('MumboJumbo',
                    (3,4,6,9,12,15,18,21),
                    (50,60,70,80,90,95,95,100),
                    (20,20,20,20,20,20,20,20)))},
 'ac': {'name': TTLocalizer.SuitAmbulanceChaser,
        'singularname': TTLocalizer.SuitAmbulanceChaserS,
        'pluralname': TTLocalizer.SuitAmbulanceChaserP,
        'level': 3,
        'hp':(30,42,56,72,90,110,132,156),
        'def':(15,20,25,30,35,40,45,50),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(65,70,75,80,85,90,95,100),
        'attacks':
                (('Shake',
                    (4,6,9,12,15,18,21,24),
                    (75,75,75,75,75,75,75,75),
                    (15,15,15,15,15,15,15,15)),
                ('RedTape',
                    (6,8,12,15,19,24,29,34),
                    (75,75,75,75,75,75,75,75),
                    (30,30,30,30,30,30,30,30)),
                ('Rolodex',
                    (3,4,5,6,7,8,9,10),
                    (75,75,75,75,75,75,75,75),
                    (20,20,20,20,20,20,20,20)),
                ('HangUp',
                    (2,3,4,5,6,7,8,9),
                    (75,75,75,75,75,75,75,75),
                    (35,35,35,35,35,35,35,35)))},
 'bs': {'name': TTLocalizer.SuitBackStabber,
        'singularname': TTLocalizer.SuitBackStabberS,
        'pluralname': TTLocalizer.SuitBackStabberP,
        'level': 4,
        'hp':(42,56,72,90,110,132,156,198),
        'def':(20,25,30,35,40,45,50,55),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('GuiltTrip',
                    (8,11,13,15,18,21,24,27),
                    (60,75,80,85,90,95,95,95),
                    (40,40,40,40,40,40,40,40)),
                ('RestrainingOrder',
                    (6,7,9,11,13,15,17,19),
                    (50,65,70,75,90,95,95,95),
                    (25,25,25,25,25,25,25,25)),
                ('FingerWag',
                    (5,6,7,8,9,10,11,12),
                    (50,55,65,75,80,85,85,85),
                    (35,35,35,35,35,35,35,35)))},
 'sd': {'name': TTLocalizer.SuitSpinDoctor,
        'singularname': TTLocalizer.SuitSpinDoctorS,
        'pluralname': TTLocalizer.SuitSpinDoctorP,
        'level': 5,
        'hp':(56,72,90,110,132,156,198,224),
        'def':(25,30,35,40,45,50,55,60),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('ParadigmShift',
                    (9,10,13,16,17,20,23,26),
                    (60,75,80,85,90,95,95,95),
                    (30,30,30,30,30,30,30,30)),
                ('Quake',
                    (8,10,12,14,16,18,20,22),
                    (60,65,70,75,80,85,85,85),
                    (20,20,20,20,20,20,20,20)),
                ('Spin',
                    (10,12,15,18,20,22,25,28),
                    (70,75,80,85,90,95,95,95),
                    (35,35,35,35,35,35,35,35)),
                ('WriteOff',
                    (6,7,8,9,10,11,12,13),
                    (60,65,75,85,90,95,95,95),
                    (15,15,15,15,15,15,15,15)))},
 'le': {'name': TTLocalizer.SuitLegalEagle,
        'singularname': TTLocalizer.SuitLegalEagleS,
        'pluralname': TTLocalizer.SuitLegalEagleP,
        'level': 6,
        'hp':(72,90,110,132,156,198,224,254),
        'def':(30,35,40,45,50,55,60,65),
        'freq':(50,30,10,5,5,5,5,5),
        'acc':(35,40,45,50,55,60,65,70),
        'attacks':
                (('EvilEye',
                    (10,11,13,15,16,18,20,22),
                    (60,75,80,85,90,95,95,95),
                    (20,20,20,20,20,20,20,20)),
                ('Jargon',
                    (7,9,11,13,15,18,21,24),
                    (60,70,75,80,90,95,95,95),
                    (15,15,15,15,15,15,15,15)),
                ('Legalese',
                    (11,13,16,19,21,24,27,30),
                    (55,65,75,85,95,95,95,95),
                    (35,35,35,35,35,35,35,35)),
                ('PeckingOrder',
                    (12,15,17,19,22,25,28,31),
                    (70,75,80,85,95,95,95,95),
                    (30,30,30,30,30,30,30,30)))},
 'bw': {'name': TTLocalizer.SuitBigWig,
        'singularname': TTLocalizer.SuitBigWigS,
        'pluralname': TTLocalizer.SuitBigWigP,
        'level': 7,
        'hp':(90,110,132,156,198,224,254,286,320,356,394,434,476,500),
        'def':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
        'freq':(50,30,10,5,5),
        'acc':(35,40,45,50,55,60,65,70,70,70,70,70,70,70),
        'attacks':
                (('PowerTrip',
                    (10,11,13,15,16,18,20,21,23,24,25,25,26,27),
                    (75,80,85,90,95,95,95,95,95,95,95,95,95,95),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)),
                ('ThrowBook',
                    (13,15,17,19,21,23,25,27,29,32,34,36,38,40),
                    (80,85,85,85,90,90,90,90,95,95,95,95,95,95),
                    (50,50,50,50,50,50,50,50,50,50,50,50,50,50)))}}

ATK_TGT_UNKNOWN = 1
ATK_TGT_SINGLE = 2
ATK_TGT_GROUP = 3
SuitAttacks = {'Audit': ('phone', ATK_TGT_SINGLE),
 'Bite': ('throw-paper', ATK_TGT_SINGLE),
 'BounceCheck': ('throw-paper', ATK_TGT_SINGLE),
 'OffenseMode': ('throw-paper', ATK_TGT_SINGLE),
 'BrainStorm': ('effort', ATK_TGT_SINGLE),
 'BuzzWord': ('speak', ATK_TGT_SINGLE),
 'Calculate': ('phone', ATK_TGT_SINGLE),
 'Canned': ('throw-paper', ATK_TGT_SINGLE),
 'Chomp': ('throw-paper', ATK_TGT_SINGLE),
 'CigarSmoke': ('cigar-smoke', ATK_TGT_SINGLE),
 'ClipOnTie': ('throw-paper', ATK_TGT_SINGLE),
 'Crunch': ('throw-object', ATK_TGT_SINGLE),
 'Demotion': ('magic1', ATK_TGT_SINGLE),
 'DoubleTalk': ('speak', ATK_TGT_SINGLE),
 'Downsize': ('magic2', ATK_TGT_SINGLE),
 'EvictionNotice': ('throw-paper', ATK_TGT_SINGLE),
 'EvilEye': ('glower', ATK_TGT_SINGLE),
 'Filibuster': ('speak', ATK_TGT_SINGLE),
 'FillWithLead': ('pencil-sharpener', ATK_TGT_SINGLE),
 'FingerWag': ('finger-wag', ATK_TGT_SINGLE),
 'Fired': ('magic2', ATK_TGT_SINGLE),
 'FiveOClockShadow': ('glower', ATK_TGT_SINGLE),
 'FloodTheMarket': ('glower', ATK_TGT_SINGLE),
 'FountainPen': ('pen-squirt', ATK_TGT_SINGLE),
 'FreezeAssets': ('glower', ATK_TGT_SINGLE),
 'Gavel': ('gavel', ATK_TGT_SINGLE),
 'GlowerPower': ('glower', ATK_TGT_SINGLE),
 'GuiltTrip': ('magic1', ATK_TGT_GROUP),
 'HalfWindsor': ('throw-paper', ATK_TGT_SINGLE),
 'HangUp': ('phone', ATK_TGT_SINGLE),
 'HeadShrink': ('magic1', ATK_TGT_SINGLE),
 'HotAir': ('speak', ATK_TGT_SINGLE),
 'Jargon': ('speak', ATK_TGT_SINGLE),
 'Legalese': ('speak', ATK_TGT_SINGLE),
 'Liquidate': ('magic1', ATK_TGT_SINGLE),
 'MarketCrash': ('throw-paper', ATK_TGT_SINGLE),
 'MumboJumbo': ('speak', ATK_TGT_SINGLE),
 'ParadigmShift': ('magic2', ATK_TGT_GROUP),
 'PeckingOrder': ('throw-object', ATK_TGT_SINGLE),
 'PickPocket': ('pickpocket', ATK_TGT_SINGLE),
 'PinkSlip': ('throw-paper', ATK_TGT_SINGLE),
 'PlayHardball': ('throw-paper', ATK_TGT_SINGLE),
 'PoundKey': ('phone', ATK_TGT_SINGLE),
 'PowerTie': ('throw-paper', ATK_TGT_SINGLE),
 'PowerTrip': ('magic1', ATK_TGT_GROUP),
 'BurnOut': ('magic1', ATK_TGT_GROUP),
 'Promotion': ('magic1', ATK_TGT_GROUP),
 'Quake': ('quick-jump', ATK_TGT_GROUP),
 'RazzleDazzle': ('smile', ATK_TGT_SINGLE),
 'RedTape': ('throw-object', ATK_TGT_SINGLE),
 'ReOrg': ('magic3', ATK_TGT_SINGLE),
 'RestrainingOrder': ('throw-paper', ATK_TGT_SINGLE),
 'Rolodex': ('roll-o-dex', ATK_TGT_SINGLE),
 'RubberStamp': ('rubber-stamp', ATK_TGT_SINGLE),
 'RubOut': ('hold-eraser', ATK_TGT_SINGLE),
 'Sacked': ('throw-paper', ATK_TGT_SINGLE),
 'SandTrap': ('golf-club-swing', ATK_TGT_SINGLE),
 'Schmooze': ('speak', ATK_TGT_SINGLE),
 'Shake': ('stomp', ATK_TGT_GROUP),
 'Shred': ('shredder', ATK_TGT_SINGLE),
 'SongAndDance': ('song-and-dance', ATK_TGT_SINGLE),
 'Spin': ('magic3', ATK_TGT_SINGLE),
 'Synergy': ('magic3', ATK_TGT_GROUP),
 'AdvancedSynergy': ('magic3', ATK_TGT_GROUP),
 'Tabulate': ('phone', ATK_TGT_SINGLE),
 'TeeOff': ('golf-club-swing', ATK_TGT_SINGLE),
 'ThrowBook': ('throw-object', ATK_TGT_SINGLE),
 'Tremor': ('stomp', ATK_TGT_GROUP),
 'Watercooler': ('watercooler', ATK_TGT_SINGLE),
 'Withdrawal': ('magic1', ATK_TGT_SINGLE),
 'WriteOff': ('hold-pencil', ATK_TGT_SINGLE)}
AUDIT = SuitAttacks.keys().index('Audit')
BITE = SuitAttacks.keys().index('Bite')
BOUNCE_CHECK = SuitAttacks.keys().index('BounceCheck')
OFFENSE_MODE = SuitAttacks.keys().index('OffenseMode')
BURN_OUT = SuitAttacks.keys().index('BurnOut')
PROMOTION = SuitAttacks.keys().index('Promotion')
BRAIN_STORM = SuitAttacks.keys().index('BrainStorm')
BUZZ_WORD = SuitAttacks.keys().index('BuzzWord')
CALCULATE = SuitAttacks.keys().index('Calculate')
CANNED = SuitAttacks.keys().index('Canned')
CHOMP = SuitAttacks.keys().index('Chomp')
CIGAR_SMOKE = SuitAttacks.keys().index('CigarSmoke')
CLIPON_TIE = SuitAttacks.keys().index('ClipOnTie')
CRUNCH = SuitAttacks.keys().index('Crunch')
DEMOTION = SuitAttacks.keys().index('Demotion')
DOWNSIZE = SuitAttacks.keys().index('Downsize')
DOUBLE_TALK = SuitAttacks.keys().index('DoubleTalk')
EVICTION_NOTICE = SuitAttacks.keys().index('EvictionNotice')
EVIL_EYE = SuitAttacks.keys().index('EvilEye')
FILIBUSTER = SuitAttacks.keys().index('Filibuster')
FILL_WITH_LEAD = SuitAttacks.keys().index('FillWithLead')
FINGER_WAG = SuitAttacks.keys().index('FingerWag')
FIRED = SuitAttacks.keys().index('Fired')
FIVE_O_CLOCK_SHADOW = SuitAttacks.keys().index('FiveOClockShadow')
FLOOD_THE_MARKET = SuitAttacks.keys().index('FloodTheMarket')
FOUNTAIN_PEN = SuitAttacks.keys().index('FountainPen')
FREEZE_ASSETS = SuitAttacks.keys().index('FreezeAssets')
GAVEL = SuitAttacks.keys().index('Gavel')
GLOWER_POWER = SuitAttacks.keys().index('GlowerPower')
GUILT_TRIP = SuitAttacks.keys().index('GuiltTrip')
HALF_WINDSOR = SuitAttacks.keys().index('HalfWindsor')
HANG_UP = SuitAttacks.keys().index('HangUp')
HEAD_SHRINK = SuitAttacks.keys().index('HeadShrink')
HOT_AIR = SuitAttacks.keys().index('HotAir')
JARGON = SuitAttacks.keys().index('Jargon')
LEGALESE = SuitAttacks.keys().index('Legalese')
LIQUIDATE = SuitAttacks.keys().index('Liquidate')
MARKET_CRASH = SuitAttacks.keys().index('MarketCrash')
MUMBO_JUMBO = SuitAttacks.keys().index('MumboJumbo')
PARADIGM_SHIFT = SuitAttacks.keys().index('ParadigmShift')
PECKING_ORDER = SuitAttacks.keys().index('PeckingOrder')
PICK_POCKET = SuitAttacks.keys().index('PickPocket')
PINK_SLIP = SuitAttacks.keys().index('PinkSlip')
PLAY_HARDBALL = SuitAttacks.keys().index('PlayHardball')
POUND_KEY = SuitAttacks.keys().index('PoundKey')
POWER_TIE = SuitAttacks.keys().index('PowerTie')
POWER_TRIP = SuitAttacks.keys().index('PowerTrip')
QUAKE = SuitAttacks.keys().index('Quake')
RAZZLE_DAZZLE = SuitAttacks.keys().index('RazzleDazzle')
RED_TAPE = SuitAttacks.keys().index('RedTape')
RE_ORG = SuitAttacks.keys().index('ReOrg')
RESTRAINING_ORDER = SuitAttacks.keys().index('RestrainingOrder')
ROLODEX = SuitAttacks.keys().index('Rolodex')
RUBBER_STAMP = SuitAttacks.keys().index('RubberStamp')
RUB_OUT = SuitAttacks.keys().index('RubOut')
SACKED = SuitAttacks.keys().index('Sacked')
SANDTRAP = SuitAttacks.keys().index('SandTrap')
SCHMOOZE = SuitAttacks.keys().index('Schmooze')
SHAKE = SuitAttacks.keys().index('Shake')
SHRED = SuitAttacks.keys().index('Shred')
SONG_AND_DANCE = SuitAttacks.keys().index('SongAndDance')
SPIN = SuitAttacks.keys().index('Spin')
SYNERGY = SuitAttacks.keys().index('Synergy')
ADVANCED_SYNERGY = SuitAttacks.keys().index('AdvancedSynergy')
TABULATE = SuitAttacks.keys().index('Tabulate')
TEE_OFF = SuitAttacks.keys().index('TeeOff')
THROW_BOOK = SuitAttacks.keys().index('ThrowBook')
TREMOR = SuitAttacks.keys().index('Tremor')
WATERCOOLER = SuitAttacks.keys().index('Watercooler')
WITHDRAWAL = SuitAttacks.keys().index('Withdrawal')
WRITE_OFF = SuitAttacks.keys().index('WriteOff')

def getFaceoffTaunt(suitName, doId):
    if suitName in SuitFaceoffTaunts:
        taunts = SuitFaceoffTaunts[suitName]
    else:
        taunts = TTLocalizer.SuitFaceoffDefaultTaunts
    return taunts[doId % len(taunts)]


SuitFaceoffTaunts = OTPLocalizer.SuitFaceoffTaunts

def getAttackTauntIndexFromIndex(suit, attackIndex):
    adict = getSuitAttack(suit.getStyleName(), suit.getLevel(), attackIndex)
    return getAttackTauntIndex(adict['name'])


def getAttackTauntIndex(attackName):
    if attackName in SuitAttackTaunts:
        taunts = SuitAttackTaunts[attackName]
        return random.randint(0, len(taunts) - 1)
    else:
        return 1


def getAttackTaunt(attackName, index = None):
    if attackName in SuitAttackTaunts:
        taunts = SuitAttackTaunts[attackName]
    else:
        taunts = TTLocalizer.SuitAttackDefaultTaunts
    if index != None:
        if index >= len(taunts):
            notify.warning('index exceeds length of taunts list in getAttackTaunt')
            return TTLocalizer.SuitAttackDefaultTaunts[0]
        return taunts[index]
    else:
        return random.choice(taunts)
    return


SuitAttackTaunts = TTLocalizer.SuitAttackTaunts

SuitStatusNames = ['lured', 'soaked', 'trapped', 'dmg-down', 'immune']

TRAPPED_STATUS = 'trapped'
LURED_STATUS = 'lured'
SOAKED_STATUS = 'soaked'
MARKED_STATUS = 'marked'
DMG_DOWN_STATUS = 'dmg-down'
IMMUNE_STATUS = 'immune'

SuitStatuses = [{'name': TRAPPED_STATUS, 'level': -1, 'damage': 0, 'toon': 0},
                {'name': LURED_STATUS, 'rounds': 1, 'kbBonus': 0.5, 'decay': 100, 'toons': [], 'levels': []},
                {'name': SOAKED_STATUS, 'rounds': 1, 'defense': -15},
                {'name': MARKED_STATUS, 'rounds': 2, 'stacks': 0, 'damage-mod': 0.0},
                {'name': DMG_DOWN_STATUS, 'rounds': 1, 'power-mod': 0.4},
                {'name': IMMUNE_STATUS, 'rounds': 2}]
ROUND_STATUSES = [LURED_STATUS, SOAKED_STATUS, MARKED_STATUS, DMG_DOWN_STATUS, IMMUNE_STATUS]


def genSuitStatus(name):
    statusEffect = None
    for status in SuitStatuses:
        if name == status['name']:
            statusEffect = copy.deepcopy(status)
    return statusEffect

def makeStatusString(status):
    dg = PyDatagram()
    dg.addString(status['name'])
    if status['name'] in ROUND_STATUSES:
        dg.addInt16(status['rounds'])
    if status['name'] == TRAPPED_STATUS:
        dg.addInt8(status['level'])
        dg.addInt32(status['damage'])
    elif status['name'] == LURED_STATUS:
        dg.addFloat32(status['kbBonus'])
        dg.addInt8(status['decay'])
    elif status['name'] == SOAKED_STATUS:
        dg.addInt16(status['defense'])
    elif status['name'] == MARKED_STATUS:
        dg.addFloat32(status['damage-mod'])

    return dg.getMessage()


def getStatusFromString(statusString):
    dg = PyDatagram(statusString)
    dgi = PyDatagramIterator(dg)
    status = genSuitStatus(dgi.getString())
    if status['name'] in ROUND_STATUSES:
        status['rounds'] = dgi.getInt16()
    if status['name'] == TRAPPED_STATUS:
        status['level'] = dgi.getInt8()
        status['damage'] = dgi.getInt32()
    elif status['name'] == LURED_STATUS:
        status['kbBonus'] = dgi.getFloat32()
        status['decay'] = dgi.getInt8()
    elif status['name'] == SOAKED_STATUS:
        status['defense'] = dgi.getInt16()
    elif status['name'] == MARKED_STATUS:
        status['damage-mod'] = dgi.getFloat32()
    return status