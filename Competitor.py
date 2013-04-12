import Rpcontest_Consts as CNT
import RpExceptions as EXC
import os,pickle
from BaseObject import *
from JudgeResult import CompetitorResult

class Competitor(workObject):
    def __init__(self,path,Name,OutputHandle):
        workObject.__init__(self,OutputHandle)

        self.Name = Name

        self.Path = os.path.abspath(path)
        self.SrcPath = self.Path + r'/' + CNT.PATH_D_SRC + r'/' + self.Name
        self.ResultPath = self.Path + r'/' + CNT.PATH_D_RESULT + r'/' + self.Name

        if not os.path.isdir(self.SrcPath):
            raise EXC.CompetitorNotFoundError(self.Name)

        if not os.path.isdir(self.ResultPath):
            os.makedirs(self.ResultPath)

        self.CpRet = CompetitorResult()

    def __cmp__(self,b):
        _make = lambda x: [
                -x.GetResult().GetTotalScore(),
                x.GetResult().GetTotalTime(),
                x.GetName()
            ]
        return cmp(_make(self),_make(b))

    def SetResult(self,cpret): self.CpRet = cpret
    def SetName(self,Name): self.Name = str(Name)

    def GetResult(self):    return self.CpRet
    def GetName(self):  return self.Name
    def GetSrcPath(self): return self.SrcPath
    def GetResultPath(self): return self.ResultPath

    def SaveResult(self):
        ret_file = self.ResultPath + r"/" + CNT.PATH_F_CPRESULT % self.Name

        if not os.path.isdir(self.ResultPath):
            os.makedirs(self.ResultPath)

        fd = open(ret_file,"w")
        pickle.dump(self.CpRet,fd)
        fd.close()

    def ReadResult(self):
        self.CpRet = CompetitorResult()
        ret_file = self.ResultPath + r'/' + CNT.PATH_F_CPRESULT % self.Name

        if not os.path.isfile(ret_file):
            return

        fd = open(ret_file,"r")
        self.CpRet = pickle.load(fd)
        fd.close()

    def HasJudged(self,TaskName):
        if not self.CpRet: return False
        return TaskName in self.GetResult().TaskResultList
