import RpExceptions as EXC
import Rpcontest_Consts as CNT

def ColorResult(txt):
    return {
        CNT.JUDGE_RESULT_AC     : CNT.EXPORT_RESULT_COLOR_AC,
        CNT.JUDGE_RESULT_WA     : CNT.EXPORT_RESULT_COLOR_WA,
        CNT.JUDGE_RESULT_RE     : CNT.EXPORT_RESULT_COLOR_RE,
        CNT.JUDGE_RESULT_TLE    : CNT.EXPORT_RESULT_COLOR_TLE,
        CNT.JUDGE_RESULT_MLE    : CNT.EXPORT_RESULT_COLOR_MLE
    }.get(txt,CNT.EXPORT_RESULT_COLOR_DEF),txt

def CalcContestAvgScore(con):
    TotScore = 0.0
    for cp in con.GetCompetitorList():
        TotScore += cp.GetResult().GetTotalScore()
    return TotScore / float(len(con.GetCompetitorList()))

class _HTML_WORKER:
    def __init__(self):
        self.buf = ''
        self.indent = 0
    def __iadd__(self,txt):
        if txt.count("<") == 1 and txt.find("/") != -1:
            self.indent -= 1;
        self.buf += "\t"*self.indent + txt + '\n'
        if txt.count("<") == 1 and txt.find("/") == -1:
            self.indent += 1
        return self
    def __str__(self):
        return self.buf

def html_start():
    return \
"""
<!DOCTYPE html>
<html>
<a name="__top__"></a>
"""
def html_end():
    return '</html>'

def get_head(title):
    return \
    "<title>%s</title>" % title + \
"""
<head>
    <style type="text/css">
    .odd {background-color : #ADDBE6;}
    .even {background-color : #FFE4C4;}

    .ACMark{color : #CB0000;}
    .Normal{color : #000080;}
    .AVGStyle {color : #000000;}
    .TopStyle {text-align:left; font-size:16px; color : #191970}

    a:link, a:visited {text-decoration:none;}
    a:hover {text-decoration:none;color:#F000FF;}

    th {text-align: center;background-color: #ADFF2F;font-size: 14px;font-weight:bold;}

    td {text-align: center;font-size: 14px;}
    td.Summary {text-align:center;}
    td.Unjudged {color:Grey}

    h1 {text-align:center;color : #000000}
    h2 {text-align:center;color : #000000}
    table.Contest{margin:auto;width:80%;}
    table.Competitor{margin:auto;width:40%;}
    p {text-align:center;font-size:20px; font-weight:bold}
    </style>
</head>
"""

def get_java_script():
    return \
"""
<script type="text/javascript">
    function get_cmp_func(colID,sortType) {
        function convert(x) {
            switch(sortType) {
                case "rank":
                    return parseInt(x);
                case "score":
                    return parseFloat(x);
                case "time":
                    return parseFloat(x.slice(0,x.length - 1))
                case "name":
                    return x.toLowerCase()
                case "task":
                    if(x=="UnJudged") {
                        return -10000000.0
                    }
                    buf = x.slice(0,x.search(/\(/))
                    score = parseFloat(buf)
                    buf = x.slice(x.search(/\(/) + 1,x.search(/s/))
                    time = parseFloat(buf)
                    return score * 100000.0 - time
            }
        }
        function get_elem(x) {
            if(x.textContent) {
                return x.textContent;
            }
            return x.innerText;
        }
        return function __compare(row1,row2) {
            var a = get_elem(row1.cells[colID]);
            var b = get_elem(row2.cells[colID]);

            var val1 = convert(a);
            var val2 = convert(b);

            if(val1 < val2) {
                return -1;
            } else if(val1 > val2) {
                return 1;
            } else {
                return 0;
            }
        };
    }

    function sortTable(tableID,colID,sortType) {
        var table = document.getElementById(tableID);
        var tbody = table.tBodies[0];
        var _ROWS = tbody.rows;
        var arr = new Array;

        for(var i = 0;i < _ROWS.length - 2;i ++) {
            arr[i] = _ROWS[i];
        }
        AVG = _ROWS[_ROWS.length - 2]
        AC = _ROWS[_ROWS.length - 1]

        if(table.lastSortColID == colID) {
            arr.reverse()
        } else {
            arr.sort(get_cmp_func(colID,sortType));
        }
        arr[_ROWS.length - 2] = AVG
        arr[_ROWS.length - 1] = AC

        Fragment = document.createDocumentFragment();
        for(var i = 0;i < arr.length;i ++) {
            if (i % 2 == 0)
                arr[i].className = "even"
            else
                arr[i].className = "odd"
            Fragment.appendChild(arr[i])
        }
        tbody.appendChild(Fragment);
        table.lastSortColID = colID;
    }
</script>
"""

def body_start():
    return '<body bgcolor = Lavender>\n'
def body_end():
    return '</body>\n'

def get_top_mark():
    return '<a class="TopStyle" href="#__top__">TOP</a>'

def deal_contest(contest,flag_Merge):
    RWidth=5
    NWidth=10
    LWidth=20

    ret = _HTML_WORKER()
    ret += get_java_script()
    ret += '<h1>Rank List</h1>'
    ret += '<table class="Contest" id="Contest">'
    # Header
    ret += '<thead>'
    ret += "<tr>"
    ret += '<th width=%d%% onclick="sortTable(\'Contest\',0,\'rank\');" style="cursor:pointer">Rank</th>' % RWidth
    ret += '<th width=%d%% onclick="sortTable(\'Contest\',1,\'name\');" style="cursor:pointer">Name</th>' % LWidth
    ret += '<th width=%d%% onclick="sortTable(\'Contest\',2,\'score\');" style="cursor:pointer">Score</th>' % NWidth
    ret += '<th width=%d%% onclick="sortTable(\'Contest\',3,\'time\');" style="cursor:pointer">Time</th>' % NWidth
    plen = (100 - RWidth - NWidth * 2 - LWidth) / len(contest.GetTaskList())
    j = 0
    for p in contest.GetTaskList():
        ret += '<th width=%d%% onclick="sortTable(\'Contest\',%d,\'task\');" style="cursor:pointer">%s</th>' % (plen,4+j,p.GetTaskName())
        j += 1
    ret += "</tr>"
    ret += '</thead>'
    # End Header
    # Competitors
    ret += '<tbody>'
    rank = 0
    for cp in contest.GetCompetitorList():
        rank += 1
        ret += '<tr class="%s">' % ("even" if rank % 2 else "odd")
        ret += "<td width=%d%%><b>%d</b></td>" % (RWidth,rank)
        ret += '<td width=%d%%><a class="%s" href="%s">%s</a></td>' % (
                LWidth,
                "ACMark" if cp.GetResult().IsAK() else "Normal",
                ("#__%s__" if flag_Merge else "%s/result.html") % cp.GetName(),
                cp.GetName())
        ret += "<td width=%d%%>%s</td>" % (RWidth,cp.GetResult().FormatTotalScore())
        ret += "<td width=%d%%>%ss</td>" % (RWidth,cp.GetResult().FormatTotalTime())
        # Tasks
        for tk in contest.GetTaskList():
            if cp.HasJudged(tk.GetTaskName()):
                ret += '<td width=%d%% class="%s">%s (%ss)</td>' % (
                    plen,
                    "ACMark" if cp.GetResult().GetTaskResult(tk.GetTaskName()).IsAC() else "Normal",
                    cp.GetResult().GetTaskResult(tk.GetTaskName()).FormatTotalScore(),
                    cp.GetResult().GetTaskResult(tk.GetTaskName()).FormatTotalTime()
                )
            else:
                ret += '<td width=%d%% class="Unjudged">UnJudged</td>' % plen
        # End Tasks
        ret += '</tr>'
    # End Competitors
    rank += 1
    # Deal Tasks
    ret += '<tr class="%s">' % ("odd" if (rank + 1) % 2 else "even")
    ret += '<td width=%d%% class="AVGStyle"><b>AVG</b></td>' % RWidth
    ret += '<td width=%d%% class="AVGStyle"> - </td>' % NWidth
    ret += '<td width=%d%% class="AVGStyle"> %.3f </td>' % (NWidth,CalcContestAvgScore(contest))
    ret += '<td width=%d%% class="AVGStyle"> - </td>' % NWidth
    for tk in contest.GetTaskList():
        totscore = 0.0
        for cp in contest.GetCompetitorList():
            if tk in cp.GetResult().GetResultList():
                totscore += tk.GetTotalScore()
        ret += '<td width=%d%% class="AVGStyle"> %.3f </td>' % (NWidth,totscore / float(len(contest.GetCompetitorList())))
    ret += '</tr>'
    # End tasks
    # Deal AC
    ret += '<tr class="%s">' % ("odd" if (rank + 2) % 2 else "even")
    ret += '<td width=%d%% class="AVGStyle"><b>%%AC</b></td>' % RWidth
    ret += '<td width=%d%% class="AVGStyle"> %.3f%% </td>' % (
            NWidth,
            float(len([1 for x in contest.GetCompetitorList() if x.GetResult().IsAK()]))\
            / float(len(contest.GetCompetitorList())) * 100.0
        )
    ret += '<td width=%d%% class="AVGStyle"> - </td>' % NWidth
    ret += '<td width=%d%% class="AVGStyle"> - </td>' % NWidth
    for tk in contest.GetTaskList():
        totscore = 0.0
        for cp in contest.GetCompetitorList():
            if tk in cp.GetResult().GetResultList() :
                totscore += tk.GetTotalScore()
        ret += '<td width=%d%% class="AVGStyle"> %.3f%% </td>' % (
                NWidth,
                float(len([1 for x in contest.GetCompetitorList()
                    if x.HasJudged(tk.GetTaskName())
                    and x.GetResult().GetTaskResult(tk.GetTaskName()).IsAC()]))\
                / float(len(contest.GetCompetitorList())) * 100.0
            )
    ret += '</tr>'

    # End AC
    ret += '</tbody>'
    ret += "</table>"
    ret += get_top_mark()
    ret += "<hr><br>"
    return str(ret)

def deal_competitor(cp,contest,flag_Merge):
    ret = _HTML_WORKER()
    ret += '<a name="__%s__"></a>' % (cp.GetName())
    ret += '<h2>Judge Details for %s</h2>' % (cp.GetName())
    for tk in contest.GetTaskList():
        ret += '<p>Details for %s</p>' % tk.GetTaskName()
        ret += '<table class="Competitor">'
        ret += '<thead>'
        ret += '<tr>'
        ret += '<th width=5%>#</th>'
        ret += '<th width=5%>Index</th>'
        ret += '<th width=30%>Result</th>'
        ret += '<th width=20%>Time</th>'
        ret += '<th width=20%>Memory</th>'
        ret += '<th width=20%>Score</th>'
        ret += '</tr>'
        ret += '</thead>'

        ret += '<tbody>'
        if cp.HasJudged(tk.GetTaskName()):
            i = 0
            cj = cp.GetResult().GetTaskResult(tk.GetTaskName())
            totscore = 0.0
            if cj.IsCompilingError():
                i += 1
                ret += '<tr class = "odd">'
                ret += '<td colspan=6>Compiling Error</td>'
                ret += '</tr>'
            elif cj.IsSrcNotFound():
                i += 1
                ret += '<tr class = "odd">'
                ret += '<td colspan=6>Source File not Found</td>'
                ret += '</tr>'
            else:
                for pnt in cj.GetResultList():
                    ret += '<tr class="%s">' % ("even" if i % 2 else "odd")
                    ret += '<td width=5%%>%d</td>' % i
                    ret += '<td width=5%%>%d</td>' % pnt.GetIndex()
                    ret += '<td style="width:30%%;color:%s">%s</td>' % ColorResult(pnt.GetResult())
                    ret += '<td width=20%%>%s s</td>' % pnt.FormatTimeCost()
                    ret += '<td width=20%%>%s kb</td>' % pnt.FormatMemCost()
                    ret += '<td width=20%%>%s</td>' % pnt.FormatScore()
                    ret += '</tr>'
                    i += 1
            ret += '<tr class="%s">' % ("even" if i % 2 else "odd")
            ret += '<td colspan=5 class="Summary">Total Score of %s</td><td class="Summary">%s</td>' % (tk.GetTaskName(),cj.FormatTotalScore())
            ret += '</tr>'
        else:
            ret += '<tr class="odd">'
            ret += '<td colspan=6>Unjudged</td>'
            ret += '</tr>'
        ret += '</tbody>'
        ret += '</table>'
    ret += '<p>Total Score of %s is %s</p>' % (cp.GetName(),cp.GetResult().FormatTotalScore())
    if flag_Merge:
        ret += get_top_mark()
    ret += "<hr><br>"
    return str(ret)
