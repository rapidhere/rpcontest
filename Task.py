import Rpcontest_Consts as CNT
import RpExceptions as EXC
from TestPoint import TestPoint
from BaseObject import *
import copy,os

class Task(workObject):
    def __init__(self,path,TaskName,OutputHandle):
        workObject.__init__(self,OutputHandle)

        self.Path = os.path.abspath(path)
        self.DataPath = self.Path + r'/' + CNT.PATH_D_DATA

        self.TaskName = TaskName
        self.Src = CNT.TK_DEF_SRC % TaskName
        self.SrcIn = CNT.TK_DEF_SRCIN % TaskName
        self.SrcOut = CNT.TK_DEF_SRCOUT % TaskName

        self.Points = set()

    def SaveTask(self):
        rtc_filename = CNT.TK_DEF_RTC_FILENAME % self.TaskName

        fp = open(self.Path + r'/' + rtc_filename,"w")

        fp.write(CNT.RTC_KEY_SRCIN + " " + self.SrcIn + "\n")
        fp.write(CNT.RTC_KEY_SRCOUT + " " + self.SrcOut + "\n")
        fp.write(CNT.RTC_KEY_SRC + " " + self.Src + "\n")

        Pnts = self.GetPointList()
        Visited = [False for i in range(0,len(Pnts))]

        for i in range(0,len(Pnts)):
            if Visited[i]: continue
            SamePnts = []
            for j in range(i,len(Pnts)):
                if Pnts[i] == Pnts[j]:
                    SamePnts.append(Pnts[j])
                    Visited[j] = True
            Indexes = [x.GetIndex() for x in SamePnts]
            Indexes.sort()

            p = 0
            PointSetString = CNT.RTC_KEY_POINTSET + " "
            while p < len(Indexes):
                q = p
                while q + 1 < len(Indexes) and \
                        Indexes[q + 1] - Indexes[p] == q + 1 - p:
                    q += 1
                PointSetString += ("%d,%d;" % (Indexes[p],Indexes[q]))
                p = q + 1
            fp.write(PointSetString + "\n")
            fp.write(repr(Pnts[i]))

    def ReadTask(self):
        def PrintWarning(txt):
            self.PrintWarning("<Line %d> in rtc_file of %s:%s" % (LineIndex,self.TaskName,txt))

        def DealPoint(IndexSet,Pnt):
            for Index in IndexSet:
                for i in range(Index[0],Index[1] + 1):
                    Pnt.SetIndex(i)
                    try:
                        Pnt.Check(self.GetDataPath(),self.TaskName)
                    except EXC.FileNotFoundError:
                        raise EXC.InvalidInputOutputFile(self.TaskName,LineIndex)
                    self.AddPoint(Pnt)

        self.__init__(self.Path,self.TaskName,self.OutputHandle)

        rtc_filename = CNT.TK_DEF_RTC_FILENAME % self.TaskName

        if not os.path.isfile(self.Path + r'/' + rtc_filename):
            raise EXC.rtcFileNotFoundError(self.TaskName)

        flag_Global = True
        LineIndex = 0

        IndexSet = []
        Pnt = TestPoint()
        for line in open(self.Path + r'/' + rtc_filename):
            LineIndex += 1

            line = line.rstrip()
            if len(line) == 0: continue

            line = line.split()
            if len(line) == 1:
                PrintWarning("EmptyKey %s,Skipped" % line[0])
                continue

            key,content = line[0],line[1]

            if flag_Global:
                if key == CNT.RTC_KEY_SRCIN:
                    self.SetSrcIn(content)
                elif key == CNT.RTC_KEY_SRCOUT:
                    self.SetSrcOut(content)
                elif key == CNT.RTC_KEY_SRC:
                    self.SetSrc(content)
                elif key == CNT.RTC_KEY_POINTSET:
                    try:
                        IndexSet = [(int(x.split(",")[0]),int(x.split(",")[1]))
                                for x in content.split(";") if len(x.rstrip())]
                    except Exception:
                        raise EXC.InvalidPointSet(self.TaskName,LineIndex)
                    flag_Global = False
                else:
                    PrintWarning("Unknown key %s in Global Area,Omitted" % key)
            else:
                if key == CNT.RTC_KEY_POINTSET:
                    DealPoint(IndexSet,Pnt)
                    Pnt = TestPoint()
                    try:
                        IndexSet = [(int(x.split(",")[0]),int(x.split(",")[1]))
                                for x in content.split(";") if len(x.rstrip())]
                    except Exception:
                        raise EXC.InvalidPointSet(self.TaskName,LineIndex)
                elif key == CNT.RTC_TPKEY_TIMELIM:
                    Pnt.SetTimeLimit(content)
                elif key == CNT.RTC_TPKEY_MEMLIM:
                    Pnt.SetMemLimit(content)
                elif key == CNT.RTC_TPKEY_INPUT:
                    Pnt.SetInput(content)
                elif key == CNT.RTC_TPKEY_OUTPUT:
                    Pnt.SetOutput(content)
                elif key == CNT.RTC_TPKEY_SCORE:
                    Pnt.SetScore(content)
                elif key == CNT.RTC_TPKEY_CMPMODE:
                    Checker = None
                    if len(line) > 2: Checker = line[2]
                    if Checker: Pnt.SetCmpMode(content,Checker)
                    else: Pnt.SetCmpMode(content)
                else:
                    PrintWarning("Unkown key %s in PointSet,Omitted" % key)

        if IndexSet: DealPoint(IndexSet,Pnt)

    def SetSrc(self,Src):           self.Src = str(Src)
    def SetSrcIn(self,SrcIn):       self.SrcIn = str(SrcIn)
    def SetSrcOut(self,SrcOut):     self.SrcOut = str(SrcOut)
    def SetTaskName(self,tkname):   self.TaskName = str(tkname)

    def GetSrc(self):           return self.Src
    def GetSrcIn(self):         return self.SrcIn
    def GetSrcOut(self):        return self.SrcOut
    def GetTaskName(self):      return self.TaskName
    def GetDataPath(self):      return self.DataPath + r'/' + self.TaskName
    def GetPoint(self,Index):
        for tp in self.Points:
            if tp.Index == Index:
                return copy.deepcopy(tp)
        return None

    def GetPointList(self): return sorted(self.Points,key=lambda k:k.Index)

    def AddPoint(self,tp):
        self.Points |= {copy.deepcopy(tp)}

    def RemovePoint(self,Index):
        for tp in self.Points:
            if tp.Index == Index:
                self.Points.remove(tp)
                break

if __name__ == "__main__":
    pnt = TestPoint()
    #task = Task("./","Test",baseOutputHandle())
    #for i in range(0,10):
    #    pnt.SetIndex(i)
    #    task.AddPoint(pnt)
    #task.SaveTask()
    task = Task("./","Test",baseOutputHandle())
    try:
        task.ReadTask()
    except EXC.rtcFileReadError,x:
        print x.FormatErrorText()
