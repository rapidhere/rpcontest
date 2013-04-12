import Rpcontest_Consts as CNT
import RpExceptions as EXC
from BaseObject import *

class SpotResult(dataObject):
    def __init__(self):
        dataObject.__init__(self)

    def SetIndex(self,Index):
        try:
            self.Index = Index
        except ValueError:
            raise EXC.FormatError("Error While Formating Index")

    def SetTimeCost(self,TimeCost):
        try:
            self.TimeCost = float(TimeCost)
        except ValueError:
            raise EXC.FormatError("Error While Formating TimeCost")

    def SetMemCost(self,MemCost):
        try:
            self.MemCost = int(MemCost)
        except ValueError:
            raise EXC.FormatError("Error While Formating MemCost")

    def SetScore(self,Score):
        try:
            self.Score = float(Score)
        except ValueError:
            raise EXC.FormatError("Error While Formating Score")

    def SetResult(self,Result):
        self.Result = Result

    def SetAC(self,Flag):
        self.AC_Flag = Flag

    def IsAC(self): return self.AC_Flag
    def GetTimeCost(self): return self.TimeCost
    def GetMemCost(self): return self.MemCost
    def GetScore(self): return self.Score
    def GetResult(self):return self.Result
    def GetIndex(self): return self.Index

    def FormatTimeCost(self):return "%.3f" % self.TimeCost
    def FormatMemCost(self): return str(self.MemCost)
    def FormatScore(self): return "%.3f" % self.Score
    def FormatResult(self):return str(self.Result)

class TaskResult(dataObject):
    def __init__(self,TaskName):
        dataObject.__init__(self)
        self.TaskName = TaskName
        self.ResultList = {}

        self.flag_SrcNotFound = False
        self.flag_CompilingError = False

    def SetSrcNotFound(self,flag = True): self.flag_SrcNotFound = flag
    def SetCompilingError(self,flag = True): self.flag_CompilingError = flag
    def IsSrcNotFound(self): return self.flag_SrcNotFound
    def IsCompilingError(self):  return self.flag_CompilingError

    def AddSpotResult(self,Index,sp):
        self.ResultList[Index] = sp

    def RemoveSpotResult(self,Index):
        if Index in self.ResultList:
            self.ResultList.pop(Index)

    def GetResultList(self):
        return [self.ResultList[x] for x in self.ResultList]

    def IsAC(self):
        if self.IsSrcNotFound() or self.IsCompilingError(): return False
        for Index in self.ResultList:
            if not self.ResultList[Index].IsAC():
                return False
        return True

    def GetTotalTime(self):
        TotTime = 0.0
        for Index in self.ResultList:
            if self.ResultList[Index].IsAC():
                TotTime += self.ResultList[Index].GetTimeCost()
        return TotTime

    def GetTotalScore(self):
        TotScore = 0.0
        for Index in self.ResultList:
            TotScore += self.ResultList[Index].GetScore()
        return TotScore

    def FormatTotalTime(self):  return "%.3f" % self.GetTotalTime()
    def FormatTotalScore(self): return "%.3f" % self.GetTotalScore()

class CompetitorResult(dataObject):
    def __init__(self):
        dataObject.__init__(self)
        self.TaskResultList = {}

    def AddTaskResult(self,tk_res):
        self.TaskResultList[tk_res.TaskName] = tk_res

    def RemoveTaskResult(self,tk_res):
        if tk_res.TaskName in self.TaskResultList:
            self.TaskResultList.pop(tk_res.TaskName)

    def GetTaskResult(self,TaskName):
        return self.TaskResultList.get(TaskName,None)

    def GetResultList(self):
        return [self.TaskResultList[x] for x in self.TaskResultList]

    def IsAK(self):
        if not len(self.TaskResultList): return False
        for tk_name in self.TaskResultList:
            if not self.TaskResultList[tk_name].IsAC():
                return False
        return True

    def GetTotalTime(self):
        TotTime = 0.0
        for tk_name in self.TaskResultList:
            TotTime += self.TaskResultList[tk_name].GetTotalTime()
        return TotTime

    def GetTotalScore(self):
        TotScore = 0.0
        for tk_name in self.TaskResultList:
            TotScore += self.TaskResultList[tk_name].GetTotalScore()
        return TotScore

    def FormatTotalScore(self): return "%.3f" % self.GetTotalScore()
    def FormatTotalTime(self):  return "%.3f" % self.GetTotalTime()
