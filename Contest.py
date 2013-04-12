import RpExceptions as EXC
import Rpcontest_Consts as CNT
from BaseObject import *
from Task import Task
from Competitor import Competitor
from JudgeResult import *
import os,time,tempfile,shutil,subprocess,sys

class Contest(workObject):
    def __init__(self,Path,OutputHandle):
        workObject.__init__(self,OutputHandle)

        self.SetPath(Path)

    def Reload(self):
        rpc_FileName = self.rpc_FileName
        self.__init__(self.Path,self.GetOutputHandle())
        self.LoadrpcFile(rpc_FileName)

    def LoadrpcFile(self,rpc_FileName):
        def PrintWarning(Text):
            self.PrintWarning("<Line %d> in rpc_file %s - %s" % \
                    (LineIndex,self.rpc_FileName,Text)
                )
        self.rpc_FileName = rpc_FileName

        self.Title = None
        self.TaskList = None
        self.CompetitorList = None

        if not os.path.isfile(self.GetPath() + r'/' + self.rpc_FileName):
            raise EXC.rpcFileNotFoundError(self.rpc_FileName,self.Path)
        self.GetOutputHandle().PrintRuntimeInfo("Reading rpc_file ...")

        LineIndex = 0
        for line in open(self.GetPath() + r'/' + self.rpc_FileName):
            line = line.rstrip()

            if len(line) == 0: continue
            line = line.split()
            key,content = line[0],line[1:]


            if key == CNT.RPC_KEY_TITLE:
                if not content:
                    self.PrintWarning("EmptyKey %s,SKipped" % key)
                    continue
                self.SetTitle(content[0])
            elif key == CNT.RPC_KEY_TASK:
                self.ClearTaskList()
                self.GetOutputHandle().PrintRuntimeInfo("\nAdd Tasks ...")
                for tk_name in content: self.AddTask(tk_name)
            elif key == CNT.RPC_KEY_COMPETITOR:
                self.ClearCompetitorList()
                self.GetOutputHandle().PrintRuntimeInfo("\nAdd Competitors ...")
                for name in content: self.AddCompetitor(name)
            else:
                PrintWarning("Unknown Key %s,Omitted" % key)

        if self.Title == None: raise EXC.KeyTitleNotFound(self.Getrpc())
        if self.TaskList == None: raise EXC.KeyTaskNotFound(self.Getrpc())
        if self.CompetitorList == None: raise EXC.KeyCompetitorNotFound(self.Getrpc())

        self.GetOutputHandle().PrintRuntimeInfo("")

    def SaverpcFile(self):
        fd = open(self.GetPath() + r'/' + self.rpc_FileName,"w")

        fd.write(CNT.RPC_KEY_TITLE + " " + self.GetTitle() + "\n")

        fd.write(CNT.RPC_KEY_TASK + " ")
        for tk in self.GetTaskList():
            fd.write(tk.GetTaskName() + " ")
        fd.write("\n")

        fd.write(CNT.RPC_KEY_COMPETITOR + " ")
        for cp in self.GetCompetitorList():
            fd.write(cp.GetName() + " ")
        fd.write("\n")

    def SaveContest(self):
        self.SaverpcFile()
        for tk in self.GetTaskList():
            tk.SaveTask()

    def SetTitle(self,Title): self.Title = str(Title)
    def SetPath(self,Path):   self.Path = os.path.abspath(Path)

    def ClearTaskList(self):  self.TaskList = []
    def ClearCompetitorList(self): self.CompetitorList = []

    def IndexTask(self,tk_name):
        Index = 0
        for tk in self.TaskList:
            if tk.GetTaskName() == tk_name:
                return Index
            Index += 1
        return -1

    def IndexCompetitor(self,name):
        Index = 0
        for cp in self.CompetitorList:
            if cp.GetName() == name:
                return Index
            Index += 1
        return -1

    def GetTitle(self):     return self.Title
    def GetTaskList(self):  return self.TaskList
    def GetCompetitorList(self):    return self.CompetitorList
    def GetPath(self):      return self.Path
    def Getrpc(self):       return self.rpc_FileName

    def AddCompetitor(self,Name):
        cp = Competitor(self.GetPath(),Name,self.GetOutputHandle())
        cp.ReadResult()
        self.GetOutputHandle().PrintRuntimeInfo("  Add Competitor %s" % cp.GetName())
        self.CompetitorList.append(cp)

    def AddTask(self,tk_name):
        tk = Task(self.GetPath(),tk_name,self.GetOutputHandle())
        tk.ReadTask()
        self.GetOutputHandle().PrintRuntimeInfo("  Add Task %s" % tk.GetTaskName())
        self.TaskList.append(tk)

    def RemoveCompetitor(self,Name):
        for cp in self.CompetitorList:
            if cp.GetName() == Name:
                self.GetOutputHandle().PrintRuntimeInfo("  Remove Competitor %s" % cp.GetName())
                self.CompetitorList.remove(cp)
                break
        return

    def RemoveTask(self,tk_name):
        for tk in self.TaskList:
            if tk.GetTaskName() == tk_name:
                self.GetOutputHandle().PrintRuntimeInfo("  Remove Task %s" % tk.GetTaskName())
                self.TaskList.remove(tk)
                break
        return

    def AbortJudge(self): self.Abort = True

    def Judge(self,
            JudgeTask = None,
            JudgeCompetitor = None,
            flag_OmitJudged = False,
            flag_FastJudge = False
        ):
        self.Abort = False

        if JudgeTask == None: JudgeTask = range(0,len(self.GetTaskList()))
        if JudgeCompetitor == None:
            JudgeCompetitor = range(0,len(self.GetCompetitorList()))

        tmp = JudgeTask[:]
        JudgeTask = []
        for Index in tmp:
            if Index in range(0,len(self.GetTaskList())):
                JudgeTask.append(Index)

        tmp = JudgeCompetitor[:]
        JudgeCompetitor = []
        for Index in tmp:
            if Index in range(0,len(self.GetCompetitorList())):
                JudgeCompetitor.append(Index)

        if len(JudgeTask) == 0 or len(JudgeCompetitor) == 0:
            raise EXC.JudgeNothinTodoError()

        PrintJudgeInfo = self.GetOutputHandle().PrintJudgeInfo
        Process = self.GetOutputHandle().Process

        JudgedCompetitor = 0
        self.GetOutputHandle().PrintRuntimeInfo("Start Judge ...")

        for CompetitorIndex in JudgeCompetitor:
            if self.Abort: return

            Process(JudgedCompetitor,len(JudgeCompetitor))
            cp = self.GetCompetitorList()[CompetitorIndex]
            cp_result = CompetitorResult()

            PrintJudgeInfo(0,"Judging Competitor %s ...\n" % cp.GetName())

            for TaskIndex in JudgeTask:
                if self.Abort: return

                tk = self.GetTaskList()[TaskIndex]
                PrintJudgeInfo(0,"Judging Task %s of %s ...\n" % (
                            tk.GetTaskName(),cp.GetName()
                        ))
                if cp.HasJudged(tk.GetTaskName()) and flag_OmitJudged:
                    PrintJudgeInfo(1,"Judged and Skipped ...\n")
                    cp_result = AddTaskResult(
                            cp.GetResult().GetTaskResult(tk.GetTaskName())
                        )
                else:
                    tk_result = self.JudgeSingleTask(cp,tk)
                    cp_result.AddTaskResult(tk_result)
                if self.Abort: return

                PrintJudgeInfo(0,"Score : %s\n" % tk_result.FormatTotalScore())
                PrintJudgeInfo(0,"\n")

            PrintJudgeInfo(0,"Total Score of %s : %s[in %s seconds]\n\n" % (
                    cp.GetName(),
                    cp_result.FormatTotalScore(),
                    cp_result.FormatTotalTime()
                ))
            if not flag_FastJudge: time.sleep(CNT.JUDGE_SLEEP_TIME)
            cp.SetResult(cp_result)
            cp.SaveResult()

            JudgedCompetitor += 1
        self.GetOutputHandle().EndJudge()

    def Export(self,flag_Merge = False,flag_ForceExport = False):
        import HtmlSupport as hs

        if not flag_ForceExport:
            for cp in self.GetCompetitorList():
                for tk in self.GetTaskList():
                    if not cp.HasJudged(tk.GetTaskName()):
                        raise EXC.ExportNotAllJudgedError()

        self.GetOutputHandle().PrintRuntimeInfo("Sorting ...")
        self.CompetitorList.sort()

        self.GetOutputHandle().PrintRuntimeInfo("Exporting ...")
        fd = open(self.GetPath() + r'/' + CNT.PATH_D_RESULT + r'/' + CNT.PATH_F_EXRESULT,"w")
        fd.write(hs.html_start())
        fd.write(hs.get_head("Judge Result - " + self.GetTitle()))
        #fd.write(hs.get_java_script())
        fd.write(hs.body_start())
        fd.write(hs.deal_contest(self,flag_Merge))

        self.GetOutputHandle().PrintRuntimeInfo("Exporting Competitors ...")
        for cp in self.GetCompetitorList():
            self.GetOutputHandle().PrintRuntimeInfo("  Competitor - %s" % cp.GetName())
            if flag_Merge:
                fd.write(hs.deal_competitor(cp,self,flag_Merge))
            else:
                cfd = open(cp.GetResultPath() + r'/' + CNT.PATH_F_EXRESULT,"w")
                cfd.write(hs.html_start())
                cfd.write(hs.get_head("Details for " + cp.GetName()))
                cfd.write(hs.body_start())
                cfd.write(hs.deal_competitor(cp,self,flag_Merge))
                cfd.write(hs.body_end())
                cfd.write(hs.html_end())
                cfd.close()

        fd.write(hs.body_end())
        fd.write(hs.html_end())
        fd.close()


    def JudgeSingleTask(self,cp,tk):
        PrintJudgeInfo = self.GetOutputHandle().PrintJudgeInfo

        tk_result = TaskResult(tk.GetTaskName())
        JudgeDir = tempfile.mkdtemp()
        try:
            SrcFile = self.GetSrcFile(cp,tk)
            if not SrcFile:
                tk_result.SetSrcNotFound()
                PrintJudgeInfo(1,"Source File is Not Found\n")
                return tk_result
            PrintJudgeInfo(0,"Found Source File ...\n")
            shutil.copy(cp.GetSrcPath() + r'/' + SrcFile,JudgeDir)

            PrintJudgeInfo(0,"Compiling ...\n")
            RunExeCmd = self.Compile(JudgeDir,SrcFile)
            if not RunExeCmd:
                tk_result.SetCompilingError()
                PrintJudgeInfo(1,"Compiling Error\n")
                return tk_result

            Number = 0
            for spot in tk.GetPointList():
                if self.Abort: return

                PrintJudgeInfo(1,"At Spot #%d : " % Number)
                spot_result = self.JudgeSingleSpot(JudgeDir,RunExeCmd,tk,spot)

                if self.Abort: return
                tk_result.AddSpotResult(spot_result.GetIndex(),spot_result)
                Number += 1
        finally:
            shutil.rmtree(JudgeDir)
        return tk_result

    def GetSrcFile(self,cp,tk):
        for EXT in CNT.SRC_EXT_LIST:
            c_src = tk.GetSrc() + r'.' + EXT
            if os.path.isfile(cp.GetSrcPath() + r'/' + c_src):
                return c_src
        return None

    def Compile(self,JudgeDir,SrcFile):
        ExeFileName = tempfile.mktemp(dir="")
        BaseName,EXT_NAME = SrcFile.split(".")[0],SrcFile.split(".")[-1]

        if EXT_NAME == CNT.EXT_TYPE_CPP:
            if os.system(CNT.COMPILE_CMD_PREFIX + CNT.COMPILE_CMD_DEF_CPP % (
                    JudgeDir + r'/' + SrcFile,JudgeDir + r'/' + ExeFileName
                )) != 0:
                return None
            return CNT.JUDGE_RUN_CMD_CPP % (JudgeDir,ExeFileName)
        elif EXT_NAME == CNT.EXT_TYPE_C:
            if os.system(CNT.COMPILE_CMD_PREFIX + CNT.COMPILE_CMD_DEF_C % (
                    JudgeDir + r'/' + SrcFile,JudgeDir + r'/' + ExeFileName
                )) != 0:
                return None
            return CNT.JUDGE_RUN_CMD_C % (JudgeDir,ExeFileName)
        elif EXT_NAME == CNT.EXT_TYPE_PAS:
            if os.system(CNT.COMPILE_CMD_PREFIX + CNT.COMPILE_CMD_DEF_PAS % (
                    JudgeDir + r'/' + SrcFile
                )) != 0:
                return None
            shutil.move(JudgeDir + r'/' + BaseName,JudgeDir + r'/' + ExeFileName)
            return CNT.JUDGE_RUN_CMD_PAS % (JudgeDir,ExeFileName)

    def JudgeSingleSpot(self,JudgeDir,RunExeCmd,tk,spot):
        ret = SpotResult()
        ret.SetIndex(spot.GetIndex())
        InputFile = tk.GetDataPath() + r'/' + spot.FormatInput(tk.GetTaskName())
        OutputFile = tk.GetDataPath() + r'/' + spot.FormatOutput(tk.GetTaskName())

        shutil.copy(InputFile,JudgeDir + r'/' + tk.GetSrcIn())

        if self.Abort: return

        tcost,mcost,state = self.RunSpot(RunExeCmd,spot.GetTimeLimit(),spot.GetMemLimit(),JudgeDir)

        if self.Abort: return

        ret.SetTimeCost(tcost)
        ret.SetMemCost(mcost)

        if state != 0:
            ret.SetResult(CNT.JUDGE_RESULT_RE)
            ret.SetScore(0)
        elif tcost > spot.GetTimeLimit():
            ret.SetResult(CNT.JUDGE_RESULT_TLE)
            ret.SetScore(0)
        elif mcost > spot.GetMemLimit():
            ret.SetResult(CNT.JUDGE_RESULT_MLE)
            ret.SetScore(0)
        else:
            Score,Msg = self.Compare(
                JudgeDir,
                OutputFile,
                JudgeDir + r'/' + tk.GetSrcOut(),
                InputFile,
                spot.GetScore(),
                spot.GetCmpMode()[0],
                spot.GetCmpMode()[1]
            )
            ret.SetResult(Msg)
            ret.SetScore(Score)

        if ret.GetScore() == spot.GetScore():
            ret.SetAC(True)
        else:
            ret.SetAC(False)
        self.GetOutputHandle().PrintJudgeInfo(2,
                "Time = %5ss Memory = %8skB %s Score = %s\n" % (
                    ret.FormatTimeCost(),
                    ret.FormatMemCost(),
                    ret.FormatResult().center(20),
                    ret.FormatScore()
                )
            )
        return ret

    def RunSpot(self,RunExeCmd,tlim,mlim,JudgeDir):
        cwd = os.getcwd()
        os.chdir(JudgeDir)

        try:
            tlim += 0.1
            mlim += 1024

            mcost = 0
            tcost = 0
            start = time.time()

            fd = open(JudgeDir + r'/__tmp__.out',"w")

            process = subprocess.Popen(RunExeCmd,stderr=fd,stdout=fd)
            mcost = self.GetMemory(process.pid)

            while process.poll() is None:
                if self.Abort: return

                time.sleep(.001)
                tcost = time.time() - start
                mcost = max(mcost,self.GetMemory(process.pid))

                self.GetOutputHandle().Timer(tcost,tlim - 0.1)
                if mcost > mlim or tcost > tlim:
                    process.kill()
                    break
            return tcost,mcost,max(0,process.poll())
        finally:
            os.chdir(cwd)

    def GetMemory(self,PID):
        for line in open("/proc/%s/status" % PID):
            if line.find("VmPeak") == -1: continue
            return int(line[
                    line.find("VmPeak:") + len("VmPeak:"):
                    line.find(" kB")
                ])
        return 0

    def Compare(self,JudgeDir,stdOutput,usrOutput,stdInput,FullScore,CmpMode,CheckerPath):
        def Compare_Ignore():
            if not os.path.isfile(usrOutput): return False
            usrfd = open(usrOutput)
            stdfd = open(stdOutput)

            while True:
                stdLine = ""
                while not len(stdLine):
                    stdLine = stdfd.readline()
                    if stdLine == "":
                        if usrfd.readline() != "": return False
                        return True
                stdLine = stdLine.rstrip()

                usrLine = ""
                while not len(usrLine):
                    usrLine = usrfd.readline()
                    if usrLine == "":
                        return False
                usrLine = usrLine.rstrip()

                if usrLine != stdLine: return False
            return True


        def Compare_Total():
            if not os.path.isfile(usrOutput): return False
            import filecmp
            return filecmp.cmp(stdOutput,stdInput)

        def Compare_UserDefine():
            shutil.copy(CheckerPath,JudgeDir)
            open(JudgeDir + r'/' + CNT.CMP_SCORE_FILE,"w").write(str(FullScore))
            open(JudgeDir + r'/' + CNT.CMP_PATH_STDOUT,"w").write(stdOutput)
            open(JudgeDir + r'/' + CNT.CMP_PATH_USROUT,"w").write(usrOutput)
            open(JudgeDir + r'/' + CNT.CMP_PATH_STDIN,"w").write(stdInput)

            if os.system(JudgeDir + r'/' + os.path.basename(CheckerPath)) != 0:
                raise EXC.JudgeUserDefineCheckerError()

            if not os.path.isfile(JudgeDir + r'/' + CNT.CMP_RESULT_SCORE):
                raise EXC.JudgeUserDefineCheckerError()
            if not os.path.isfile(JudgeDir + r'/' + CNT.CMP_RESULT_MSG):
                raise EXC.JudgeUserDefineCheckerError()
            try:
                Score = float(open(JudgeDir + r'/' + CNT.CMP_RESULT_SCORE).readline())
                Msg = open(JudgeDir + r'/' + CNT.CMP_RESULT_MSG).readline().rstrip()
            except ValueError,TypeError:
                raise EXC.JudgeUserDefineCheckerError()
            return Score,Msg

        if CmpMode == CNT.CMPMODE_IGNORE:
            if Compare_Ignore():
                return FullScore,CNT.JUDGE_RESULT_AC
            return 0,CNT.JUDGE_RESULT_WA
        elif CmpMode == CNT.CMPMODE_TOTAL:
            if Compare_Total():
                return FullScore,CNT.JUDEG_RESULT_AC
            return 0,CNT.JUDGE_RESULT_WA
        elif CmpMode == CNT.CMPMODE_USERDEF:
            return Compare_UserDefine()
