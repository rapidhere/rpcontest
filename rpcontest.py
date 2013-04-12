#!/usr/bin/python
from optparse import OptionParser
import rpc
import os,sys
import grpcontest

parser = OptionParser(
    usage="%prog -o rpc_file <Options> or %prog -g",
    description = rpc.Description,
    epilog = "Call me on rapidhere@gmail.com",
    version = "rpcontest - " + rpc.version
)

parser.add_option(
    "-g","--gui-frame",
    action="store_true",default=False,
    help="Open rpcontest with a GUI-Frame.Will omit other options"
)

parser.add_option(
    "-o","--open",
    metavar="rpcFileName",dest="rpcFile",
    help="Open a rpcFile to do something with it"
)

parser.add_option(
    "-j","--judge",
    action="store_true",default=False,
    help="Judge the Contest"
)

parser.add_option(
    "-e","--export",
    action="store_true",default=False,
    help="Export the Judge Result as a html file"
)

parser.add_option(
    "-c","--competitor",
    metavar="CompetitorNames",dest="Competitor",default=None,
    help="Use with -j/--judge.Specify the Competitors to be judged,split by comma"
)

parser.add_option(
    "-t","--task",
    metavar="TaskNames",dest="Task",default=None,
    help="Use with -j/--judge.Specify the Tasks to be judged,spilt by comma"
)

parser.add_option(
    "","--fast-judge",
    action="store_true",default=False,
    help="Use with -j/--judge.Don't wait after judged each competitor"
)

parser.add_option(
    "","--omit-judged",
    action="store_true",default=False,
    help="Use with -j/--judge.Will skip judged tasks"
)

parser.add_option(
    "","--force-export",
    action="store_true",default=False,
    help="Must export a html file even if some tasks and/or competitors are not judged"
)

parser.add_option(
    "","--merge-export",
    action="store_true",default=False,
    help="Export as a signle html file"
)

Option,Args = parser.parse_args()
parser.destroy()

class OutputHandle(rpc.baseOutputHandle):
    def __init__(self):
        rpc.baseOutputHandle.__init__(self)

    def PrintWaringInfo(self,Text):
        print "Warning : " + Text

    def PrintErrorInfo(self,Text):
        print "Error : " + Text

    def PrintRuntimeInfo(self,Text):
        sys.stderr.write(Text + "\n")

    def PrintJudgeInfo(self,Indent,Text):
        sys.stderr.write("  " * Indent + Text)

    def Timer(self,Current,Total):
        timer_str = "> [ Timer : %.3f / %.3f ] <" % (Current,Total)
        sys.stderr.write(timer_str + "\b" * len(timer_str))

    def Process(self,Current,Total):
        sys.stderr.write("=" * 80 + " %d / %d [%.3f%% Done]\n" % \
                (Current + 1,Total,float(Current) / float(Total) * 100.0)
            )

    def EndJudge(self):
        sys.stderr.write("=" * 80 + "JudgeDone\n")

if Option.gui_frame:
    grpcontest.Start()
    exit()

if not Option.rpcFile:
    print "Nothing to do!"
    exit(1)
try:
    con = rpc.Contest(os.path.dirname(Option.rpcFile),OutputHandle())
    con.LoadrpcFile(os.path.basename(Option.rpcFile))
except rpc.RpException,x:
    exit(1)
    print x.FormatErrorText()

if Option.judge:
    TaskList = Option.Task
    CompetitorList = Option.Competitor

    if TaskList:
        TaskList = []
        for tk_name in Option.Task.split(","):
            Index = con.IndexTask(tk_name)
            if Index == -1:
                print "%s is not a valid task of the contest %s" % (tk_name,con.GetTitle())
                exit(1)
            TaskList.append(Index)

    if CompetitorList:
        CompetitorList = []
        for cp_name in Option.Competitor.split(","):
            Index = con.IndexCompetitor(cp_name)
            if Index == -1:
                print "%s is not a valid competitor of contest %s" % (cp_name,con.GetTitle())
                exit(1)
            CompetitorList.append(Index)

    try:
        con.Judge(TaskList,CompetitorList,Option.omit_judged,Option.fast_judge)
    except rpc.RpException,x:
        print x.FormatErrorText()
        exit(1)

if Option.export:
    try:
        con.Export(Option.merge_export,Option.force_export)
    except rpc.RpException,x:
        print x.FormatErrorText()
        exit(1)

exit(0)
