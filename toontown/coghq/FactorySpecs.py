from toontown.toonbase import ToontownGlobals
import SellbotLegFactorySpec
import SellbotLegFactoryCogs
import SellbotLegFactoryCogsKaboomberg
import LawbotLegFactorySpec
import LawbotLegFactoryCogs

def getFactorySpecModule(factoryId):
    return FactorySpecModules[factoryId]


def getCogSpecModule(factoryId):
    return CogSpecModules[factoryId]

def getCogSpecModuleKaboomberg(factoryId):
    return CogSpecModulesKaboomberg[factoryId]


FactorySpecModules = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactorySpec,
 ToontownGlobals.LawbotOfficeInt: LawbotLegFactorySpec}
CogSpecModules = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactoryCogs,
 ToontownGlobals.LawbotOfficeInt: LawbotLegFactoryCogs}
CogSpecModulesKaboomberg = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactoryCogsKaboomberg,
 ToontownGlobals.LawbotOfficeInt: LawbotLegFactoryCogs}
if __dev__:
    import FactoryMockupSpec
    FactorySpecModules[ToontownGlobals.MockupFactoryId] = FactoryMockupSpec
    import FactoryMockupCogs
    CogSpecModules[ToontownGlobals.MockupFactoryId] = FactoryMockupCogs
