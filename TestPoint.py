import Rpcontest_Consts as CNT
import RpExceptions as EXC
from BaseObject import *
import os

class TestPoint(dataObject):
    def __init__(self):
        dataObject.__init__(self)
        self.SetIndex(0)
        self.SetTimeLimit()
        self.SetMemLimit()
        self.SetCmpMode()
        self.SetInput()
        self.SetOutput()
        self.SetScore()

    def __cmp__(self,b):
        list_key = lambda tp:[
                    tp.TimeLim,
                    tp.MemLim,
                    tp.CmpMode,
                    tp.CheckerPath,
                    tp.Input,
                    tp.Output,
                    tp.Score
                ]

        return cmp(list_key(self),list_key(b))

    def __hash__(self):
        return self.Index

    def __repr__(self):
        ret = \
            CNT.RTC_TPKEY_TIMELIM + " " + self.FormatTimeLimit() + "\n" + \
            CNT.RTC_TPKEY_MEMLIM  + " " + self.FormatMemLimit()  + "\n" + \
            CNT.RTC_TPKEY_SCORE   + " " + self.FormatScore()     + "\n" + \
            CNT.RTC_TPKEY_CMPMODE + " " + ("%s %s" % self.FormatCmpMode()) + "\n" +\
            CNT.RTC_TPKEY_INPUT   + " " + self.GetInput() + "\n" + \
            CNT.RTC_TPKEY_OUTPUT  + " " + self.GetOutput() + "\n"
        return ret

    def SetIndex(self,Index):
        try:
            self.Index = int(Index)
        except ValueError:
            raise EXC.FormatError("Index must be a Integer!")

    def SetTimeLimit(self,TLim = CNT.TP_DEF_TIMELIM):
        try:
            self.TimeLim = float(TLim)
        except ValueError:
            raise EXC.FormatError("TimeLimit must be a Float Number!")

    def SetMemLimit(self,MLim = CNT.TP_DEF_MEMLIM):
        try:
            self.MemLim = int(MLim)
        except ValueError:
            raise EXC.FormatError("MemLimit must be a Integer!")

    def SetCmpMode(self,CmpMode = CNT.TP_DEF_CMPMODE,path = ""):
        try:
            self.CmpMode = str(CmpMode)
            self.CheckerPath = str(path)
        except ValueError:
            raise EXC.FormatError("Invalid CmpMode!")

        if self.CmpMode != CNT.CMPMODE_IGNORE and self.CmpMode != CNT.CMPMODE_TOTAL:
            if self.CmpMode != CNT.CMPMODE_USERDEF:
                raise EXC.FormatError(self.CmpMode + " is Not a available cmp-mode!")

    def SetInput(self,Input = CNT.TP_DEF_INPUT):
        self.Input = str(Input)

    def SetOutput(self,Output = CNT.TP_DEF_OUTPUT):
        self.Output = str(Output)

    def SetScore(self,Score = CNT.TP_DEF_SCORE):
        try:
            self.Score = float(Score)
        except ValueError:
            raise EXC.FormatError("Score must be a Float Number!")

    def GetIndex(self):         return self.Index
    def GetTimeLimit(self):     return self.TimeLim
    def GetMemLimit(self):      return self.MemLim
    def GetCmpMode(self):       return self.CmpMode,self.CheckerPath
    def GetInput(self):         return self.Input
    def GetOutput(self):        return self.Output
    def GetScore(self):         return self.Score

    def FormatIndex(self):       return str(self.Index)
    def FormatTimeLimit(self):   return "%.3f" % self.TimeLim
    def FormatMemLimit(self):    return str(self.MemLim)
    def FormatCmpMode(self):     return self.CmpMode,str(self.CheckerPath)
    def FormatScore(self):       return "%.3f" % self.Score
    def FormatInput(self,Task):  return self.Input.replace("%s",Task) % self.Index
    def FormatOutput(self,Task): return self.Output.replace("%s",Task) % self.Index

    def Check(self,DataPath,Task):
        try:
            if not os.path.isfile(DataPath + r'/' + self.FormatInput(Task)):
                raise EXC.FileNotFoundError("Invalid Input",self.FormatInput(Task))
            if not os.path.isfile(DataPath + r'/' + self.FormatOutput(Task)):
                raise EXC.FileNotFoundError("Invalid Output",self.FormatOutput(Task))
            if self.CmpMode == CNT.CMPMODE_USERDEF and not os.path.isfile(self.CheckerPath):
                raise EXC.FileNotFoundError("Invalud Checker!",self.CheckerPath)
        except TypeError:
            raise EXC.FormatError("Input/Output syntax Error!")
        return True
