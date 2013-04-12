class RpException(Exception):
    def __init__(self):
        Exception.__init__(self)

    def SetText(self,Text):
        self.Text = Text

    def GetText(self):
        return self.Text

    def FormatErrorText(self):
        self.Text = "Error : " + self.Text
        return self.Text

    def FormatWarnText(self):
        sefl.Text = "Warning : " + self.Text
        return self.Text

class InvalidOutputHandle(RpException):
    def __init__(self):
        RpException.__init__(self)
        self.SetText("OutputHandle object must be a instance of baseOutputHandle")

class FormatError(RpException):
    def __init__(self,Text):
        RpException.__init__(self)
        self.SetText(Text)

    def SetText(self,Text):
        self.Text = "Format Error : " + Text

class rtcFileReadError(RpException):
    def __init__(self,TaskName,LineIndex):
        RpException.__init__(self)
        self.SetText(TaskName,LineIndex)

    def SetText(self,TaskName,LineIndex):
        self.Text = "<Line %d> in rtc_file of %s - %s" % (
                LineIndex,TaskName,self.__class__.__name__
            )
class InvalidPointSet(rtcFileReadError): pass
class InvalidInputOutputFile(rtcFileReadError): pass

class rpcFileReadError(RpException):
    def __init__(self,rpc_FileName):
        RpException.__init__(self)
        self.SetText(rpc_FileName)

    def SetText(self,rpc_FileName):
        self.Text = "In rpc_file %s - %s" % (
                rpc_FileName,self.__class__.__name__
            )
class KeyTitleNotFound(rpcFileReadError): pass
class KeyTaskNotFound(rpcFileReadError): pass
class KeyCompetitorNotFound(rpcFileReadError): pass

class NotFoundError(RpException): pass

class FileNotFoundError(NotFoundError):
    def __init__(self,Text,Filename):
        NotFoundError.__init__(self)
        self.SetText(Text,Filename)

    def SetText(self,Text,Filename):
        self.Text = \
            ("File Not Found Error : File `%s' is not found ," % Filename) \
            + Text

class CompetitorNotFoundError(NotFoundError):
    def __init__(self,Name):
        NotFoundError.__init__(self)
        self.SetText(Name)

    def SetText(self,Name):
        self.Text = "Competitor %s is not found" % Name

class rtcFileNotFoundError(NotFoundError):
    def __init__(self,TaskName):
        NotFoundError.__init__(self)
        self.SetText(TaskName)

    def SetText(self,TaskName):
        self.Text = "The rtc_file of %s is not found" % TaskName

class DataDirNotFoundError(NotFoundError):
    def __init__(self,TaskName):
        NotFoundError.__init__(self)
        self.SetText(TaskName)

    def SetText(self,TaskName):
        self.Text = "The data direcotry of %s is not found" % TaskName

class rpcFileNotFoundError(NotFoundError):
    def __init__(self,rpc_File,Path):
        NotFoundError.__init__(self)
        self.SetText(rpc_File,Path)

    def SetText(self,rpc_File,Path):
        self.Text = "rpc_file %s is not found under Path : %s" % (rpc_File,Path)

class JudgeError(RpException): pass
class JudgeNothinTodoError(JudgeError):
    def __init__(self):
        JudgeError.__init__(self)
        self.SetText("No thing to do In Judge!")

class JudgeUserDefineCheckerError(JudgeError):
    def __init__(self):
        JudgeError.__init__(self)
        self.SetText("User Define Checker Error!")

class ExportError(RpException): pass
class ExportNotAllJudgedError(ExportError):
    def __init__(self):
        ExportError.__init__(self)
        self.SetText("Not all Tasks and/or Competitors are Judged!")
