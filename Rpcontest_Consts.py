IPTH = "/home/rapid/Desktop/Work/python/rpcontest"
EXT_TYPE_RTC = "rtc"
EXT_TYPE_RPC = "rpc"

EXT_TYPE_CPP = "cpp"
EXT_TYPE_C = "c"
EXT_TYPE_PAS = "pas"
SRC_EXT_LIST = [EXT_TYPE_CPP,EXT_TYPE_C,EXT_TYPE_PAS]

COMPILE_CMD_PREFIX = "timeout 5 "
COMPILE_CMD_DEF_CPP = "g++ %s -o %s -Wall"
COMPILE_CMD_DEF_C   = "gcc %s -o %s -Wall"
COMPILE_CMD_DEF_PAS = "fpc %s"

CMPMODE_IGNORE  = "ignore"
CMPMODE_TOTAL   = "total"
CMPMODE_USERDEF = "UserDefine"

TP_DEF_TIMELIM  = 1.000
TP_DEF_MEMLIM   = 128 * 1024
TP_DEF_INPUT    = "%s%d.in"
TP_DEF_OUTPUT   = "%s%d.out"
TP_DEF_CMPMODE  = CMPMODE_IGNORE
TP_DEF_SCORE    = 10.000

TK_DEF_SRCIN    = "%s.in"
TK_DEF_SRCOUT   = "%s.out"
TK_DEF_SRC      = "%s"
TK_DEF_RTC_FILENAME = "%s.rtc"

RTC_TPKEY_TIMELIM   = "timelim"
RTC_TPKEY_MEMLIM    = "memlim"
RTC_TPKEY_CMPMODE   = "cmpmode"
RTC_TPKEY_INPUT     = "input"
RTC_TPKEY_OUTPUT    = "output"
RTC_TPKEY_SCORE     = "score"
RTC_KEY_POINTSET    = "pointset"
RTC_KEY_SRCIN       = "srcin"
RTC_KEY_SRCOUT      = "srcout"
RTC_KEY_SRC         = "src"
RPC_KEY_TITLE       = "title"
RPC_KEY_TASK        = "task"
RPC_KEY_COMPETITOR  = "competitor"

PATH_D_DATA     = "data"
PATH_D_SRC      = "src"
PATH_D_RESULT   = "result"
PATH_F_CPRESULT = ".%s.ret"
PATH_F_EXRESULT = "result.html"

JUDGE_SLEEP_TIME = 2.0

JUDGE_RUN_CMD_CPP   = "%s/%s"
JUDGE_RUN_CMD_C     = "%s/%s"
JUDGE_RUN_CMD_PAS   = "%s/%s"

JUDGE_RESULT_AC = "Accepted"
JUDGE_RESULT_WA = "Wrong Answer"
JUDGE_RESULT_RE = "Runtime Error"
JUDGE_RESULT_TLE = "Time Out"
JUDGE_RESULT_MLE = "Memory Out"

CMP_SCORE_FILE = "score.log"
CMP_PATH_STDOUT = "stdoutput.log"
CMP_PATH_USROUT = "usroutput.log"
CMP_PATH_STDIN = "stdinput.log"
CMP_RESULT_SCORE = "score.log"
CMP_RESULT_MSG = "message.log"

EXPORT_RESULT_COLOR_DEF= "#000000"
EXPORT_RESULT_COLOR_AC = "#007700"
EXPORT_RESULT_COLOR_WA = "#DB0000"
EXPORT_RESULT_COLOR_TLE= "#CC4400"
EXPORT_RESULT_COLOR_MLE= "#000055"
EXPORT_RESULT_COLOR_RE = "#760954"
