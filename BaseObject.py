import RpExceptions as EXC

class baseOutputHandle:
    def __init__(self): pass
    def PrintWarningInfo(self,txt): print txt
    def PrintErrorInfo(self,txt): print txt
    def PrintRuntimeInfo(self,txt): print txt

    def PrintJudgeInfo(self,Indent,Text): print "  " * Indent + Text
    def Timer(self,Current,Total): pass
    def Process(self,Current,Total): pass

    def EndJudge(self): pass

class workObject:
    def __init__(self,OutputHandle):
        self.SetOutputHandle(OutputHandle)

    def SetOutputHandle(self,cOutputHandle):
        if isinstance(cOutputHandle,baseOutputHandle):
            self.OutputHandle = cOutputHandle
        else:
            raise EXC.InvalidOutputHandle

    def GetOutputHandle(self):
        return self.OutputHandle

    def PrintWarning(self,txt): self.OutputHandle.PrintWarningInfo(txt)
    def PrintError(self,txt): self.OutputHandle.PrintErrorInfo(txt)
    def PrintRuntimeInfo(self,txt): self.OutputHandle.PrintRuntimeInfo(txt)

class dataObject:
    def __init__(self): pass
