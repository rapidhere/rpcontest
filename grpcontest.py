#!/usr/bin/python

import wx,os,sys,copy,thread,shutil
import rpc
import wx.aui,wx.gizmos

app_name = "gui-rpcontest"
version = "1.0.0.1"

def CreateLabelItem(parent,label,item):
    bsizer = wx.StaticBoxSizer(
            wx.StaticBox(parent,-1,label=label),
            wx.VERTICAL
        )
    bsizer.Add(item,1,wx.EXPAND)
    return bsizer

def PError(parent,txt):
        error_dialog = wx.MessageDialog(
                parent = parent,
                caption = "Error",
                message = txt,
                style=wx.ICON_ERROR | wx.OK
            )
        error_dialog.ShowModal()

class rpcontest_EVT_ADD_RUNTIME_INFO(wx.PyCommandEvent):
    def __init__(self,evtType,id):
        wx.PyCommandEvent.__init__(self,evtType,id)

    def GetText(self):
        return self.txt

    def SetText(self,txt):
        self.txt = txt

class rpcontest_EVT_UPDATE_DISPLAY(wx.PyCommandEvent):
    def __init__(self,evtType,id):
        wx.PyCommandEvent.__init__(self,evtType,id)

    def Set(self,UpdateType,con):
        self.UpdateType = UpdateType
        self.con = con

    def Get(self):
        return self.UpdateType,self.con

rpEVT_ADD_RUNTIME_INFO = wx.NewEventType()
EVT_ADD_RUNTIME_INFO = wx.PyEventBinder(rpEVT_ADD_RUNTIME_INFO,1)

rpEVT_UPDATE_DISPLAY = wx.NewEventType()
EVT_UPDATE_DISPLAY = wx.PyEventBinder(rpEVT_UPDATE_DISPLAY,1)

def EmitAppendRuntimeInfo(self,text):
    evt = rpcontest_EVT_ADD_RUNTIME_INFO(rpEVT_ADD_RUNTIME_INFO,self.GetId())
    evt.SetText(text)
    self.GetEventHandler().ProcessEvent(evt)

def EmitUpdateDisplay(self,t,con):
    evt = rpcontest_EVT_UPDATE_DISPLAY(rpEVT_UPDATE_DISPLAY,self.GetId())
    evt.Set(t,con)
    self.GetEventHandler().ProcessEvent(evt)

class rpcontest_CheckList(wx.Panel):
    def __init__(self,parent,size=(150,100),OnCheckListBox = None,OnChooseAll = None,OnDechooseAll = None):
        wx.Panel.__init__(self,parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SelectedIndex = []

        self.ListBox = wx.CheckListBox(self,-1,size=size)
        self.sizer.Add(self.ListBox,1,wx.EXPAND)

        hsizer = wx.BoxSizer()
        self.ChooseAllButton = wx.Button(self,-1,"Select All")
        hsizer.Add(self.ChooseAllButton,0,wx.ALIGN_RIGHT)

        self.DechooseAllButton = wx.Button(self,-1,"Deselect All")
        hsizer.Add(self.DechooseAllButton,0,wx.ALIGN_RIGHT)
        self.sizer.Add(hsizer,0,wx.EXPAND)

        self.SetSizer(self.sizer)

        if not OnChooseAll:     OnChooseAll     = self.OnChooseAll
        if not OnDechooseAll:   OnDechooseAll   = self.OnDechooseAll
        if not OnCheckListBox:  OnCheckListBox  = self.OnCheckListBox

        self.Bind(wx.EVT_BUTTON,OnChooseAll,self.ChooseAllButton)
        self.Bind(wx.EVT_BUTTON,OnDechooseAll,self.DechooseAllButton)
        self.Bind(wx.EVT_CHECKLISTBOX,OnCheckListBox,self.ListBox)

    def ClearAll(self):
        self.ListBox.Clear()
        self.SelectedIndex = []

    def Append(self,label):
        self.ListBox.Append(label)

    def GetCheckedItems(self):
        return copy.deepcopy(self.SelectedIndex)

    def OnChooseAll(self,event):
        self.SelectedIndex = range(0,self.ListBox.GetCount())
        for i in self.SelectedIndex:
            self.ListBox.Check(i)
        event.Skip()

    def OnDechooseAll(self,event):
        for i in range(0,self.ListBox.GetCount()):
            self.ListBox.Check(i,False)
        self.SelectedIndex = []
        event.Skip()

    def OnCheckListBox(self,event):
        index = event.GetSelection()
        if self.ListBox.IsChecked(index):
            self.SelectedIndex.append(index)
        else:
            self.SelectedIndex.remove(index)
        event.Skip()

class rpcontest_Gauge(wx.Panel):
    def __init__(self,parent):
        self.Width = 20
        wx.Panel.__init__(self,parent,-1)

        self.sizer = wx.BoxSizer()
        self.Gauge = wx.Gauge(self,-1,1000)
        self.sizer.Add(self.Gauge,1,wx.EXPAND)

        self.Processer = wx.StaticText(self,-1,style=wx.ALIGN_LEFT,label= " [0.000 %]".center(self.Width))
        self.sizer.Add(self.Processer,0,wx.EXPAND)

        self.SetSizer(self.sizer)

    def SetTotal(self,tot):
        self.Total = tot
        self.Current = 0

    def SetCurrent(self,cur):
        self.Current = cur
        self.Processer.SetLabel((" [%.3f %%]" % (float(self.Current) / float(self.Total) * 100.0)).center(self.Width))
        self.Gauge.SetValue(float(self.Current) / float(self.Total) * 1000)

    def Reset(self):
        self.Processer.SetLabel(" [0.000%]".center(self.Width))
        self.SetTotal(1)
        self.SetCurrent(0)


class EditSpotInfoDialog(wx.Dialog):
    def __init__(self,parent,tk,spot = None,flag_UnableEditIndex = False,IndexList = None):
        wx.Dialog.__init__(self,parent,
                id=-1,
                size=(400,500),
                title="Edit Spot details",
                style=wx.CAPTION
            )
        self.IndexList = IndexList
        self.flag_UnableEditIndex = flag_UnableEditIndex
        self.tk = tk
        if spot:
            self.spot = spot
        else:
            self.spot = rpc.TestPoint()
        self.Centre()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.AddStretchSpacer(1)
        self.sizer.Add(self.CreateWorkSpace(),0,wx.EXPAND)
        self.sizer.AddStretchSpacer(1)
        self.sizer.Add(self.CreateButtonBar(),0,wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_BUTTON,self.OnOK,self.OKButton)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.CancelButton)
        self.Bind(wx.EVT_BUTTON,self.OnChoose,self.ChooseButton)
        self.Bind(wx.EVT_CHOICE,self.OnChoice,self.CmpModeCtrl)

    def CreateWorkSpace(self):
        def CreateLabel(label,pos):
            return wx.StaticText(self.ConfigPanel,-1,label,pos=pos,size=(100,25))
        def CreateTextCtrl(pos,txt):
            return wx.TextCtrl(self.ConfigPanel,-1,pos=pos,size=(150,25),value=txt)
        self.ConfigPanel = wx.Panel(self,-1,size=(300,400))

        label = CreateLabel("Index",(50,20))
        self.IndexCtrl = CreateTextCtrl((200,20),self.spot.FormatIndex())
        if self.flag_UnableEditIndex:
            self.IndexCtrl.SetEditable(False)
            self.IndexCtrl.SetBackgroundColour("Grey")
        CreateLabel("Timelim(s)",(50,50))
        self.TimeCtrl  = CreateTextCtrl((200,50),self.spot.FormatTimeLimit())
        CreateLabel("Memlim(kb)",(50,80))
        self.MemCtrl   = CreateTextCtrl((200,80),self.spot.FormatMemLimit())
        CreateLabel("Input",(50,110))
        self.InputCtrl = CreateTextCtrl((200,110),self.spot.GetInput())
        CreateLabel("Output",(50,140))
        self.OutputCtrl= CreateTextCtrl((200,140),self.spot.GetOutput())
        CreateLabel("Score",(50,170))
        self.ScoreCtrl = CreateTextCtrl((200,170),self.spot.FormatScore())
        CreateLabel("CmpMode",(50,200))
        CreateLabel("Checker Path:",(50,230))
        self.CmpModeCtrl = wx.Choice(self.ConfigPanel,-1,pos=(150,200),size=(200,25),
                    choices=["Ignore Extra Spaces","Compare Every Character","User Define"]
                )
        self.ChooseButton = wx.Button(self.ConfigPanel,-1,pos=(270,230),size=(80,25),label="Choose")
        self.UserDefinePath = wx.TextCtrl(self.ConfigPanel,-1,
                size=(300,100),pos=(50,260),
                style=wx.TE_READONLY | wx.TE_MULTILINE
            )
        self.SetCmpModeState()

        bsizer = wx.StaticBoxSizer(
                wx.StaticBox(self,-1,label="Details"),
                wx.VERTICAL
            )
        bsizer.Add(self.ConfigPanel,0,wx.EXPAND)
        return bsizer

    def SetCmpModeState(self):
        index = 0
        if self.spot.GetCmpMode()[0] == rpc.CMPMODE_IGNORE:
            index = 0
        elif self.spot.GetCmpMode()[0] == rpc.CMPMODE_TOTAL:
            index = 1
        elif self.spot.GetCmpMode()[0] == rpc.CMPMODE_USERDEF:
            index = 2

        self.CmpModeCtrl.SetSelection(index)

        if index == 0 or index == 1:
            self.ChooseButton.Disable()
            self.UserDefinePath.Clear()
            self.UserDefinePath.SetBackgroundColour("Grey")
        else:
            self.ChooseButton.Enable()
            self.UserDefinePath.SetBackgroundColour("pink")
            self.UserDefinePath.Clear()
            self.UserDefinePath.AppendText(self.spot.GetCmpMode()[1])

    def CreateButtonBar(self):
        sizer = wx.BoxSizer()
        sizer.AddStretchSpacer(1)

        self.OKButton = wx.Button(self,-1,"OK")
        sizer.Add(self.OKButton,0)

        self.CancelButton = wx.Button(self,-1,"Cancel")
        sizer.Add(self.CancelButton,0)

        return sizer

    def OnCancel(self,event):
        self.spot = None
        self.Destroy()

    def OnOK(self,event):
        data_path = self.GetParent().con.GetPath() + r'/' + rpc.PATH_D_DATA + r'/' + self.tk.GetTaskName()

        spot = copy.deepcopy(self.spot)
        try:
            spot.SetIndex(self.IndexCtrl.GetValue())
            spot.SetTimeLimit(self.TimeCtrl.GetValue())
            spot.SetMemLimit(self.MemCtrl.GetValue())
            spot.SetInput(self.InputCtrl.GetValue())
            spot.SetOutput(self.OutputCtrl.GetValue())
            spot.SetScore(self.ScoreCtrl.GetValue())

            IndexList = self.IndexList if self.IndexList else [spot.GetIndex()]

            for Index in IndexList:
                spot.SetIndex(Index)
                spot.Check(self.tk.GetDataPath(),self.tk.GetTaskName())
        except rpc.RpException,x:
            PError(self,x.FormatErrorText())
            return
        finally:
            event.Skip()
        self.spot = spot
        self.Destroy()

    def OnChoose(self,event):
        ch = wx.FileDialog(self,
                wildcard="*.*",
                defaultDir = self.GetParent().con.GetPath(),
                message = "Choose a Checker",
                style= wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
        if ch.ShowModal() == wx.ID_OK:
            self.spot.SetCmpMode(rpc.CMPMODE_USERDEF,ch.GetPath())
        self.SetCmpModeState()
        event.Skip()

    def OnChoice(self,event):
        index = self.CmpModeCtrl.GetCurrentSelection()
        if index == 0: self.spot.SetCmpMode(rpc.CMPMODE_IGNORE)
        elif index == 1: self.spot.SetCmpMode(rpc.CMPMODE_TOTAL)
        elif index == 2: self.spot.SetCmpMode(rpc.CMPMODE_USERDEF,"")

        self.SetCmpModeState()

    def ShowDialog(self):
        self.ShowModal()
        return self.spot

class rpcontest_ConfigurePanel(wx.Panel):
    def __init__(self,parent,con):
        wx.Panel.__init__(self,parent)
        self.sizer = wx.BoxSizer()
        self.con = con

        self.sizer.Add(self.CreateTaskBar(),0,flag=wx.EXPAND)
        self.sizer.Add(self.CreateCompetitorBar(),0,flag=wx.EXPAND)
        self.sizer.Add(self.CreateTaskInfoBar(),1,flag=wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_LISTBOX,self.OnSelectTask,self.TaskListBox)
        self.Bind(wx.EVT_CHECKLISTBOX,self.OnCheckListBox,self.TaskListBox)
        self.Bind(wx.EVT_BUTTON,self.OnAddSpot,self.AddSpotButton)
        self.Bind(wx.EVT_BUTTON,self.OnEditSpot,self.EditSpotButton)
        self.Bind(wx.EVT_BUTTON,self.OnRemoveSpot,self.RemoveSpotButton)
        self.Bind(wx.EVT_BUTTON,self.OnAddOtherSpot,self.AddOtherSpotButton)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelectPoint,self.PointList)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.OnDeselectPoint,self.PointList)
        self.Bind(wx.EVT_TEXT_ENTER,self.OnChangeTitleBar,self.TitleBar)
        self.Bind(wx.EVT_TEXT_ENTER,self.OnChangeSrcFile,self.SrcBar)
        self.Bind(wx.EVT_TEXT_ENTER,self.OnChangeSrcInput,self.SrcInputBar)
        self.Bind(wx.EVT_TEXT_ENTER,self.OnChangeSrcOutput,self.SrcOutputBar)
        self.Bind(wx.EVT_CHECKLISTBOX,self.OnCheckCompetitor,self.CompetitorListBox)

    def CreateTaskBar(self):
        tsizer = wx.BoxSizer(wx.VERTICAL)

        self.TitleBar = wx.TextCtrl(self,-1,size=(150,20),style=wx.TE_PROCESS_ENTER)

        tsizer.Add(CreateLabelItem(self,"Title",self.TitleBar),
                0,flag=wx.ALIGN_LEFT | wx.TOP)

        self.TaskListBox = wx.CheckListBox(
                parent=self,
                id=-1,
                name="Tasks",
                style = wx.LB_SINGLE | wx.LB_ALWAYS_SB
            )
        tsizer.Add(CreateLabelItem(self,"Tasks",self.TaskListBox),
                1,wx.EXPAND)

        return tsizer

    def CreateCompetitorBar(self):
        self.CompetitorListBox = wx.CheckListBox(self,-1,size=(150,20))
        return CreateLabelItem(self,"Competitors",self.CompetitorListBox)

    def CreateTaskInfoBar(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        hsizer = wx.BoxSizer()
        self.TaskTitleBar = wx.TextCtrl(self,-1,size=(150,20),style=wx.TE_READONLY)
        hsizer.Add(CreateLabelItem(self,"TaskTitle",self.TaskTitleBar),
                0,wx.EXPAND)

        self.SrcBar = wx.TextCtrl(self,-1,size=(150,20),style=wx.TE_PROCESS_ENTER)
        hsizer.Add(CreateLabelItem(self,"SrcFile",self.SrcBar),
                0,wx.EXPAND)

        self.SrcInputBar = wx.TextCtrl(self,-1,size=(150,20),style=wx.TE_PROCESS_ENTER)
        hsizer.Add(CreateLabelItem(self,"SrcInput",self.SrcInputBar),
                0,wx.EXPAND)

        self.SrcOutputBar = wx.TextCtrl(self,-1,size=(150,20),style=wx.TE_PROCESS_ENTER)
        hsizer.Add(CreateLabelItem(self,"SrcOutput",self.SrcOutputBar),
                0,wx.EXPAND)
        sizer.Add(hsizer,0,wx.ALIGN_LEFT)

        sizer.Add(self.CreateSpotDetailsBar(),1,wx.EXPAND)

        return sizer

    def CreateSpotDetailsBar(self):
        self.Columns = (
            ("#",20),
            ("Index",50),
            ("Timelim(s)",-1),
            ("MemLim(kB)",-1),
            ("Input",-1),
            ("Output",-1),
            ("Score",-1),
            ("cmpmode",-1),
        )
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.PointList = wx.ListCtrl(self,-1,style=wx.LC_REPORT)
        self.SelectedIndex = []
        index = 0
        for item,width in self.Columns:
            self.PointList.InsertColumn(index,item,width=width)
            index += 1
        sizer.Add(CreateLabelItem(self,"Spots Details",self.PointList)
                ,1,wx.EXPAND)
        hsizer = wx.BoxSizer()

        self.AddSpotButton = wx.Button(self,-1,"Add Spot")
        hsizer.Add(self.AddSpotButton,0,wx.EXPAND)

        self.EditSpotButton = wx.Button(self,-1,"Edit Spot(s)")
        hsizer.Add(self.EditSpotButton,0,wx.EXPAND)

        self.AddOtherSpotButton = wx.Button(self,-1,"Add Other Spot(s)")
        hsizer.Add(self.AddOtherSpotButton,0,wx.EXPAND)
        self.AddOtherSpotButton.Disable()

        self.RemoveSpotButton = wx.Button(self,-1,"Remove Spot(s)")
        hsizer.Add(self.RemoveSpotButton,0,wx.EXPAND)

        sizer.Add(hsizer,0,wx.EXPAND)

        return sizer

    def ClearSpotDetails(self):
        self.PointList.DeleteAllItems()
        self.SelectedIndex = []
        self.TaskTitleBar.Clear()
        self.SrcBar.Clear()
        self.SrcInputBar.Clear()
        self.SrcOutputBar.Clear()
        self.AddOtherSpotButton.Disable()

    def DisplaySpotDetails(self,tk_id):
        self.ClearSpotDetails()

        tk = self.con.GetTaskList()[tk_id]
        self.TaskTitleBar.WriteText(tk.GetTaskName())
        self.SrcBar.WriteText(tk.GetSrc())
        self.SrcInputBar.WriteText(tk.GetSrcIn())
        self.SrcOutputBar.WriteText(tk.GetSrcOut())

        i = 0
        for spot in tk.GetPointList():
            index = self.PointList.InsertStringItem(sys.maxint,str(i))
            self.PointList.SetStringItem(index,1,spot.FormatIndex())
            self.PointList.SetStringItem(index,2,spot.FormatTimeLimit())
            self.PointList.SetStringItem(index,3,spot.FormatMemLimit())
            self.PointList.SetStringItem(index,4,spot.FormatInput(tk.GetTaskName()))
            self.PointList.SetStringItem(index,5,spot.FormatOutput(tk.GetTaskName()))
            self.PointList.SetStringItem(index,6,spot.FormatScore())
            self.PointList.SetStringItem(index,7,spot.FormatCmpMode()[0])
            i += 1

        if self.PointList.GetItemCount() == 0:
            self.AddOtherSpotButton.Disable()
        else:
            self.AddOtherSpotButton.Enable()

    def UpdateDisplay(self,con = None):
        self.PointList.DeleteAllItems()

        self.TaskTitleBar.Clear()
        self.SrcBar.Clear()
        self.SrcInputBar.Clear()
        self.SrcOutputBar.Clear()
        self.TitleBar.Clear()
        self.TaskListBox.Clear()
        self.CompetitorListBox.Clear()

        self.con = con
        if not self.con: return

        self.TitleBar.WriteText(self.con.GetTitle())
        for ft in os.listdir(self.con.GetPath()):
            if ft.split(".")[-1] == rpc.EXT_TYPE_RTC:
                self.TaskListBox.Append(ft[:-len(rpc.EXT_TYPE_RTC) - 1])
        tasklist = self.TaskListBox.GetStrings()
        for tk in self.con.GetTaskList():
            if tk.GetTaskName() in tasklist:
                self.TaskListBox.Check(tasklist.index(tk.GetTaskName()))

        for ft in os.listdir(self.con.GetPath() + r'/' + rpc.PATH_D_SRC):
            if os.path.isdir(self.con.GetPath() + r'/' + rpc.PATH_D_SRC + r'/' + ft):
                self.CompetitorListBox.Append(ft)
        cplist = self.CompetitorListBox.GetStrings()
        for cp in self.con.GetCompetitorList():
            if cp.GetName() in cplist:
                self.CompetitorListBox.Check(cplist.index(cp.GetName()))

    def GetSelectedTask(self):
        sel = self.TaskListBox.GetStringSelection()
        if not sel:
            return None,-1
        index = self.con.IndexTask(sel)
        if index == -1:
            return sel,-1
        return sel,index

    def OnSelectTask(self,event):
        sel,index = self.GetSelectedTask()
        EmitAppendRuntimeInfo(self,"Current Task : %s\n" % sel)
        if not sel or index ==-1: return
        self.DisplaySpotDetails(index)

    def OnCheckListBox(self,event):
        index = event.GetSelection()
        tk_name = self.TaskListBox.GetString(index)

        if self.TaskListBox.IsChecked(index):
            try:
                self.con.AddTask(str(tk_name))
                self.TaskListBox.SetSelection(index)
                self.DisplaySpotDetails(self.con.IndexTask(self.TaskListBox.GetSelection()))
            except rpc.RpException,x:
                PError(self,x.FormatErrorText())
                return
        else:
            self.con.RemoveTask(tk_name)
            self.ClearSpotDetails()
        EmitUpdateDisplay(self,"Judge",self.con)

    def OnAddSpot(self,event):
        EmitAppendRuntimeInfo(self,"Add A Spot\n")
        try:
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            dia = EditSpotInfoDialog(self,self.con.GetTaskList()[index])
            spot = dia.ShowDialog()
            if spot:
                self.con.GetTaskList()[index].AddPoint(spot)
            self.DisplaySpotDetails(index)
        finally:
            event.Skip()

    def OnSelectPoint(self,event):
        self.SelectedIndex.append(event.m_itemIndex)
        event.Skip()

    def OnDeselectPoint(self,event):
        self.SelectedIndex.remove(event.m_itemIndex)
        event.Skip()

    def OnEditSpot(self,event):
        try:
            if len(self.SelectedIndex) == 0:
                EmitAppendRuntimeInfo(self,"<WARN>No spot to edit!\n")
                return
            EmitAppendRuntimeInfo(self,"Edit Spot(s) #%s\n" % sorted(self.SelectedIndex))
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            spot = rpc.TestPoint()

            dia = EditSpotInfoDialog(self,self.con.GetTaskList()[index],
                    spot = spot,flag_UnableEditIndex = True,
                    IndexList=self.SelectedIndex
                )

            spot = dia.ShowDialog()
            if spot:
                for pos in self.SelectedIndex:
                    idx = self.con.GetTaskList()[index].GetPointList()[pos].GetIndex()
                    spot.SetIndex(idx)
                    self.con.GetTaskList()[index].RemovePoint(idx)
                    self.con.GetTaskList()[index].AddPoint(spot)
            self.DisplaySpotDetails(index)
        finally:
            event.Skip()

    def OnRemoveSpot(self,event):
        try:
            if len(self.SelectedIndex) == 0:
                EmitAppendRuntimeInfo(self,"<WARN>No spot to remove!\n")
                return
            EmitAppendRuntimeInfo(self,"Remove spot(s) #%s\n" % self.SelectedIndex)
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            if wx.MessageDialog(self,
                    message = "Remove these spots?",
                    caption = "Caution",
                    style = wx.YES_NO | wx.ICON_EXCLAMATION | wx.NO_DEFAULT
                ).ShowModal() == wx.ID_NO:
                return
            for idx in self.SelectedIndex:
                self.con.GetTaskList()[index].RemovePoint(idx)
            self.DisplaySpotDetails(index)
        finally:
            event.Skip()

    def OnAddOtherSpot(self,event):
        EmitAppendRuntimeInfo(self,"Finding ...\n")
        try:
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            Task = self.con.GetTaskList()[index]
            spot = copy.deepcopy(Task.GetPointList()[0])
            for idx in range(0,1000):
                spot.SetIndex(idx)
                try:
                    spot.Check(Task.GetDataPath(),Task.GetTaskName())
                except rpc.RpException:
                    continue
                else:
                    EmitAppendRuntimeInfo(self,"  Found new spot @Index:%d\n" % idx)
                    Task.AddPoint(spot)

            self.DisplaySpotDetails(index)
        finally:
            event.Skip()

    def OnChangeTitleBar(self,event):
        try:
            if not self.con: return
            EmitAppendRuntimeInfo(self,"New Contest Title : %s\n" % self.TitleBar.GetValue())
            self.con.SetTitle(self.TitleBar.GetValue())
        finally:
            event.Skip()

    def OnChangeSrcFile(self,event):
        try:
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            EmitAppendRuntimeInfo(self,"New Source File : %s\n" % self.SrcBar.GetValue())
            self.con.GetTaskList()[index].SetSrc(self.SrcBar.GetValue())
        finally:
            event.Skip()

    def OnChangeSrcInput(self,event):
        try:
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            EmitAppendRuntimeInfo(self,"New src input : %s\n" % self.SrcInputBar.GetValue())
            self.con.GetTaskList()[index].SetSrcIn(self.SrcInputBar.GetValue())
        finally:
            event.Skip()

    def OnChangeSrcOutput(self,event):
        try:
            sel,index = self.GetSelectedTask()
            if not sel or index == -1: return
            EmitAppendRuntimeInfo(self,"New src output : %s\n" % self.SrcOutputBar.GetValue())
            self.con.GetTaskList()[index].SetSrcOut(self.SrcOutputBar.GetValue())
        finally:
            event.Skip()

    def OnCheckCompetitor(self,event):
        index = event.GetSelection()
        cp_name = self.CompetitorListBox.GetString(index)

        if self.CompetitorListBox.IsChecked(index):
            self.con.AddCompetitor(cp_name)
        else:
            self.con.RemoveCompetitor(cp_name)
        EmitUpdateDisplay(self,"Judge",self.con)
        event.Skip()

class rpcontest_RunJudgePanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,-1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.ProcessGauge = rpcontest_Gauge(self)
        self.sizer.Add(CreateLabelItem(self,"Process",self.ProcessGauge),0,wx.EXPAND)

        self.TimerLED = wx.gizmos.LEDNumberCtrl(self,-1)
        self.TimerLED.SetValue("0.000-0.000")
        self.sizer.Add(CreateLabelItem(self,"Timer",self.TimerLED),1,wx.EXPAND)
        self.Timer_Total = 0.0
        self.Timer_Current = 0.0

        self.ProcessTextCtrl = wx.TextCtrl(self,-1,style=wx.TE_READONLY | wx.TE_MULTILINE)
        Font = wx.Font(10,wx.MODERN,wx.NORMAL,weight=10)
        self.ProcessTextCtrl.SetFont(Font)
        self.sizer.Add(self.ProcessTextCtrl,3,wx.EXPAND)

        self.sizer.Add(self.CreateButton(),0,wx.EXPAND)

        self.SetSizer(self.sizer)

        self.flag_OmitJudged = False
        self.flag_FastJudge = False

        self.Bind(wx.EVT_BUTTON,self.OnStopJudge,self.StopJudgeButton)
        self.Bind(wx.EVT_BUTTON,self.OnStartJudge,self.StartJudgeButton)

    def CreateButton(self):
        hsizer = wx.BoxSizer()

        self.StartJudgeButton = wx.Button(self,-1,label="Start Judge")
        hsizer.Add(self.StartJudgeButton,0,wx.RIGHT)

        self.StopJudgeButton = wx.Button(self,-1,label="Stop Judge")
        hsizer.Add(self.StopJudgeButton,0,wx.RIGHT)
        self.StopJudgeButton.Disable()

        return hsizer

    def UpdateTimer(self,Current,Total):
        def _UpdateTimer(self,Current,Total):
            self.TimerLED.SetValue("%.3f-%.3f " % (Current,Total))

        wx.CallAfter(_UpdateTimer,self,Current,Total)

    def UpdateProcess(self,Current,Total):
        def _UpdateProcess(self,Current,Total):
            self.ProcessGauge.SetTotal(Total)
            self.ProcessGauge.SetCurrent(Current)

        wx.CallAfter(_UpdateProcess,self,Current,Total)

    def EndJudge(self):
        def _EndJudge(self):
            self.ProcessGauge.SetCurrent(self.ProcessGauge.Total)

            self.StartJudgeButton.Enable()
            self.StopJudgeButton.Disable()

        wx.CallAfter(_EndJudge,self)

    def AddJudgeInfo(self,Text):
        def _AddJudgeInfo(self,Text):
            self.ProcessTextCtrl.AppendText(Text)

        wx.CallAfter(_AddJudgeInfo,self,Text)

    def OnStartJudge(self,event):
        self.con = self.GetParent().con
        competitors = self.GetParent().Competitors.GetCheckedItems()
        tasks = self.GetParent().Tasks.GetCheckedItems()

        if len(competitors) == 0 or len(tasks) == 0:
            return
        self.ProcessTextCtrl.Clear()

        self.td = thread.start_new_thread(
                self.con.Judge,
                (tasks,competitors,self.flag_OmitJudged,self.flag_FastJudge)
            )
        self.StartJudgeButton.Disable()
        self.StopJudgeButton.Enable()
        event.Skip()

    def OnStopJudge(self,event):
        wx.CallAfter(self.con.AbortJudge)
        self.StartJudgeButton.Enable()
        self.StopJudgeButton.Disable()

        self.ProcessGauge.Reset()

        event.Skip()

class rpcontest_JudgePanel(wx.Panel):
    def __init__(self,parent,con):
        wx.Panel.__init__(self,parent,id = -1)
        self.con = con

        self.sizer = wx.BoxSizer()

        self.sizer.Add(self.CreateJudgeInfoBox(),0,wx.EXPAND)
        self.sizer.Add(self.CreateJudgeProcessBox(),1,wx.EXPAND)

        self.SetSizer(self.sizer)

    def CreateJudgeInfoBox(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.Competitors = rpcontest_CheckList(self)
        sizer.Add(CreateLabelItem(self,"Choose Competitors:",self.Competitors),1,wx.EXPAND)

        self.Tasks = rpcontest_CheckList(self)
        sizer.Add(CreateLabelItem(self,"Choose Tasks:",self.Tasks),1,wx.EXPAND)

        return CreateLabelItem(self,"Judgement Information",sizer)

    def UpdateDisplay(self,con):
        self.con = con
        self.Competitors.ClearAll()
        self.Tasks.ClearAll()

        if not self.con: return
        for tk in self.con.GetTaskList():
            self.Tasks.Append(tk.GetTaskName())
        for cp in self.con.GetCompetitorList():
            self.Competitors.Append(cp.GetName())

    def CreateJudgeProcessBox(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.JudgePanel = rpcontest_RunJudgePanel(self)
        sizer.Add(self.JudgePanel,1,wx.EXPAND)

        return CreateLabelItem(self,"Judgement Process",sizer)

    def SetFlag_OmitJudged(self,Flag):
        self.JudgePanel.flag_OmitJudged = Flag

    def SetFlag_FastJudge(self,Flag):
        self.JudgePanel.flag_FastJudge = Flag

class rpcontest_WorkPanel(wx.Panel):
    def __init__(self,parent,frame):
        self.TabWidth = 50

        wx.Panel.__init__(self,parent,-1,style=wx.SUNKEN_BORDER)
        self.Frame = frame

        self.nb = wx.Notebook(self)
        self.config_window = rpcontest_ConfigurePanel(self.nb,self.Frame.con)
        self.nb.AddPage(self.config_window,"Config".center(self.TabWidth))

        self.judge_window = rpcontest_JudgePanel(self.nb,self.Frame.con)
        self.nb.AddPage(self.judge_window,"Judge".center(self.TabWidth))

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.nb,1,flag=wx.EXPAND)
        self.SetSizer(self.sizer)

    def UpdateDisplay(self,con):
        self.config_window.UpdateDisplay(con)
        self.judge_window.UpdateDisplay(con)

class rpcontest_Frame(wx.Frame):
    def __init__(self):
        self._Title = "%s %s" % (app_name,version)
        wx.Frame.__init__(
                self,
                parent=None,
                id=-1,
                title=self._Title,
                size=(1200,800)
            )
        self.Center()
        self._icon = wx.Icon(rpc.IPTH + r"/icon.png",wx.BITMAP_TYPE_PNG)
        self.SetIcon(self._icon)

        self.con = None

        self.CreateMenuBar()

        self.CreateWorkSpace()

        self.statusbar = self.CreateStatusBar()
        self.SetStatus()

        self.Bind(EVT_ADD_RUNTIME_INFO,self.OnAddRuntimeInfo)
        self.Bind(EVT_UPDATE_DISPLAY,self.OnUpdateDisplay)

        self.flag_MergeExport = False
        self.flag_ForceExport = False

        self.CreateOutputHandle()

    def OnAddRuntimeInfo(self,event):
        self.AddRuntimeInfo(event.GetText())

    def OnUpdateDisplay(self,event):
        t,con = event.Get()

        if t == "All":
            self.workwindow.UpdateDisplay(con)
        elif t == "Config":
            self.workwindow.config_window.UpdateDisplay(con)
        elif t == "Judge":
            self.workwindow.judge_window.UpdateDisplay(con)

    def AddRuntimeInfo(self,info):
        max_line_lenth = 512
        self.infowindow.AppendText(info)
        while self.infowindow.GetNumberOfLines() > max_line_lenth:
            self.infowindow.Remove(0,1)

    def CreateMenuBar(self):
        MenuData = \
        (
            ("&Contest",
                ("&Open Contest\tCtrl-O" ,"Open an existed contest",self.OnOpenContest),
                ("&New Contest\tCtrl-N"  ,"Create a new contest",self.OnCreateContest),
                ("&Save Contest\tCtrl-S" ,"Save Current contest",self.OnSaveContest),
                (None,None,None),
                ("&Quit\tCtrl-Q" ,"Quit rpcontest",self.OnQuit)
            ),
            ("C&ontrol",
                ("&Refresh\tF5" , "Refresh the display",self.OnRefresh),
                ("&Reload\tCtrl-F5"  , "Reload the contest",self.OnReload)
            ),
            ("&Judge",
                ("Judge Options" , "Config Your Judgement",
                    (
                        ("Don't wait after judgement","#CheckItem",self.OnCheckFastJudge),
                        ("Omit judged competitors and tasks","#CheckItem",self.OnCheckOmitJudged)
                    )
                ),
                ("Export Options", "Config Your Export Style",
                    (
                        ("Force Export","#CheckItem",self.OnCheckForceExport),
                        ("Export as a html file","#CheckItem",self.OnCheckMergeExport),
                    )
                ),
                ("Clear Results" ,"Note : Will Auto Reload the Contest",self.OnClearResult),
                ("Export Html\tCtrl-E"   , "Export As a HTML File",self.OnExportHtml),
                ("Open Report File\tCtrl-Alt-E",  "Open Report File",self.OnOpenReport)
            ),
            ("&InfoWindow",
                ("On" , "#RadioItem" , self.TurnOnInfoWindow),
                ("Off", "#RadioItem" , self.TurnOffInfoWindow)
            ),
            ("&Help",
                ("&Help Document\tF1","Help Document",self.OnHelp),
                ("&About","About",self.OnAbout)
            ),
        )
        def CreateMenu(menudata):
            menu = wx.Menu()
            for label,status,handler in menudata:
                if label == None:
                    menu.AppendSeparator()
                else:
                    if type(handler) == tuple:
                        menu.AppendMenu(-1,label,CreateMenu(handler),status)
                    elif status[0] == '#':
                        if status == '#CheckItem':
                            cmenu = menu.AppendCheckItem(-1,label,status)
                            self.Bind(wx.EVT_MENU,handler,cmenu)
                        elif status == "#RadioItem":
                            cmenu = menu.AppendRadioItem(-1,label,status)
                            self.Bind(wx.EVT_MENU,handler,cmenu)
                    else:
                        cmenu = menu.Append(-1,label,status)
                        self.Bind(wx.EVT_MENU,handler,cmenu)
            return menu

        self.menubar = wx.MenuBar()
        self.Menus = []

        for md in MenuData:
            ml,md = md[0],md[1:]
            self.Menus.append(CreateMenu(md))
            self.menubar.Append(self.Menus[-1],ml)
        self.SetMenuBar(self.menubar)

    def CreateWorkSpace(self):
        def CreateWorkWindow():
            self.workwindow = rpcontest_WorkPanel(self,self)
            self.sizer.Add(self.workwindow,proportion=2,flag = wx.EXPAND)

        def CreateInfoWindow():
            self.infowindow = wx.TextCtrl(
                    parent = self,
                    id = -1,
                    style=wx.SUNKEN_BORDER | wx.TE_MULTILINE | wx.TE_READONLY
                )
            self.infowindow.SetBackgroundColour("pink")
            Font = wx.Font(11,wx.MODERN,style=wx.NORMAL,weight=11)
            self.infowindow.SetFont(Font)
            self.__total_infowindow = CreateLabelItem(self,"Runtime Information:",self.infowindow)
            self.sizer.Add(self.__total_infowindow,
                    proportion=1,flag = wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        CreateWorkWindow()
        CreateInfoWindow()

        self.SetSizer(self.sizer)

    def SetStatus(self):
        if self.con:
            self.statusbar.SetStatusText("Contest : %s" % self.con.GetTitle())
            self.SetTitle(self._Title + " -- %s" % self.con.GetTitle())
        else:
            self.SetTitle(self._Title)
            self.statusbar.SetStatusText("Free")

    def OnOpenReport(self,event):
        if not self.con : return
        report_file = self.con.GetPath() + r'/' + rpc.PATH_D_RESULT + r"/" + rpc.PATH_F_EXRESULT
        if not os.path.isfile(report_file):
            PError(self,"No report file!")
            return
        import webbrowser
        webbrowser.open("file://"+report_file)

    def OnExportHtml(self,event):
        if self.con == None: return
        try:
            self.AddRuntimeInfo("Export report html for Contest - %s\n" % self.con.GetTitle())
            self.con.Export(
                    flag_ForceExport = self.flag_ForceExport,
                    flag_Merge = self.flag_MergeExport
                )
        except rpc.RpException,x:
            PError(self,x.FormatErrorText())

    def OnCheckFastJudge(self,event):
        self.workwindow.judge_window.SetFlag_FastJudge(
                self.menubar.IsChecked(event.GetId())
            )
        event.Skip()

    def OnCheckOmitJudged(self,event):
        self.workwindow.judge_window.SetFlag_OmitJudged(
                self.menubar.IsChecked(event.GetId())
            )
        event.Skip()

    def OnCheckForceExport(self,event):
        self.flag_ForceExport = self.menubar.IsChecked(event.GetId())
        event.Skip()

    def OnCheckMergeExport(self,event):
        self.flag_MergeExport = self.menubar.IsChecked(event.GetId())
        event.Skip()

    def TurnOffInfoWindow(self,event):
        self.__total_infowindow.Hide(self.infowindow)
        event.Skip()

    def TurnOnInfoWindow(self,event):
        self.__total_infowindow.Show(self.infowindow)
        event.Skip()

    def OnClearResult(self,event):
        if not self.con: return
        shutil.rmtree(self.con.GetPath() + r'/' + rpc.PATH_D_RESULT)
        self.OnReload(event)
        event.Skip()


    def OnOpenContest(self,event):
        chdialog = wx.FileDialog(
                parent=self,
                message="Choose A Contest",
                defaultDir="~",
                wildcard="RPC-ContestFile|*.rpc",
                style=wx.OPEN
            )
        if chdialog.ShowModal() == wx.ID_OK:
            filename = chdialog.GetPath()
            try:
                self.AddRuntimeInfo("Open Contest at : %s\n" % filename)
                self.con = rpc.Contest(os.path.dirname(filename),self.OutputHandle)
                self.con.LoadrpcFile(os.path.basename(filename))
            except rpc.RpException,x:
                self.con = None
                PError(self,x.FormatErrorText())
            self.workwindow.UpdateDisplay(self.con)
        self.SetStatus()
        chdialog.Destroy()
        event.Skip()

    def OnQuit(self,event):
        if self.con:
            self.con.AbortJudge()
        self.AddRuntimeInfo("Quit\n")
        self.Close()

    def OnSaveContest(self,event):
        if not self.con:
            self.AddRuntimeInfo("No thing to save!\n")
            return
        self.AddRuntimeInfo("Saving contest ...")
        self.con.SaveContest()
        self.AddRuntimeInfo("Done\n")

    def OnRefresh(self,event):
        if not self.con: return
        self.SetStatus()
        self.workwindow.UpdateDisplay(self.con)
        event.Skip()

    def OnReload(self,event):
        if not self.con: return
        self.con.Reload()
        self.SetStatus()
        self.workwindow.UpdateDisplay(self.con)
        event.Skip()

    def OnCreateContest(self,event):
        chdialog = wx.DirDialog(
                parent = self,
                message="Choose A Contest Menu",
                defaultPath="~"
            )
        if chdialog.ShowModal() == wx.ID_OK:
            self.CreateNewContest(chdialog.GetPath())
            self.workwindow.UpdateDisplay(self.con)
        self.SetStatus()
        chdialog.Destroy()
        event.Skip()

    def OnAbout(self,event):
        info = wx.AboutDialogInfo()
        info.Name = app_name
        info.SetIcon(self._icon)
        info.SetVersion(version)
        info.SetCopyright('(C) RapidHere RanttuInc@BunkerHill')
        info.AddDeveloper("rapidhere@gmail.com")
        info.SetDescription(
                "grpcontest:\n"
                "grpcontest is the GUI-Frame for rpcontest\n"
                "Based on rpcontest kernel %s\n" % rpc.version +
                "\n"
                "rpcontest:" +
                rpc.Description
            )

        wx.AboutBox(info)

    def CreateNewContest(self,path):
        path = os.path.abspath(path)
        if not os.path.isdir(path + r'/' + D_SRC):
            os.makedirs(path + r'/' + rpc.PATH_D_SRC)
        if not os.path.isdir(path + r'/' + D_DATA):
            os.makedirs(path + r'/' + rpc.PATH_D_DATA)

        fp = open(path + r'/' + "auto_create.rpc","w")
        fp.write(rpc.RPC_KEY_TITLE + " sample")
        fp.write(rpc.RPC_KEY_TASK + "\n" + rpc.RPC_KEY_COMPETITOR + "\n")
        fp.close()

        for mn in os.listdir(path + r'/' + rpc.PATH_D_DATA):
            if os.path.isdir(path + r'/' + rpc.PATH_D_DATA + r'/' + mn) and \
                    not os.path.isfile(path + r'/' + mn + '.' + rpc.EXT_TYPE_RTC):
                fp = open(path + r'/' + mn + '.' + rpc.EXT_TYPR_RTC,"w")
                fp.close()
        try:
            self.AddRuntimeInfo("Create New contest at : %s\n" % path)
            self.con = rpc.Contest(path,self.OutputHandle)
            self.con.LoadrpcFile("auto_create.rpc")
        except RpError,x:
            self.con = None
            PError(self,x.txt)

    def OnHelp(self,event):
        self.AddRuntimeInfo("Sorry ... But the help document is empty = =\n")

    def CreateOutputHandle(self):
        class OutputHandle(rpc.baseOutputHandle):
            def __init__(self,Frame):
                rpc.baseOutputHandle.__init__(self)
                self.Frame = Frame

            def PrintWarningInfo(self,Text):
                self.Frame.AddRuntimeInfo("Warning : " + Text)
            def PrintErrorInfo(self,Text):
                PError(self.Frame,Text)
            def PrintRuntimeInfo(self,Text):
                self.Frame.AddRuntimeInfo(Text + "\n")
            def PrintJudgeInfo(self,Indent,Text):
                self.Frame.workwindow.judge_window.JudgePanel.AddJudgeInfo(
                        "  " * Indent + Text
                    )
            def Timer(self,Current,Total):
                self.Frame.workwindow.judge_window.JudgePanel.UpdateTimer(Current,Total)
            def Process(self,Current,Total):
                self.Frame.workwindow.judge_window.JudgePanel.UpdateProcess(Current,Total)
            def EndJudge(self):
                self.Frame.AddRuntimeInfo("="*80 + "Judge Done\n")
                self.Frame.workwindow.judge_window.JudgePanel.EndJudge()
        self.OutputHandle = OutputHandle(self)

class App(wx.App):
    def OnInit(self):
        waittime = 3000
        bmp = wx.Image(rpc.IPTH + "/boot.png").ConvertToBitmap()
        wx.SplashScreen(
                bitmap = bmp,
                splashStyle = wx.SPLASH_TIMEOUT | wx.SPLASH_CENTRE_ON_SCREEN,
                milliseconds = waittime,
                parent=None,
                id=-1
            )
        wx.Yield()

        self.SetAppName(app_name)
        return True

def Start():
    app = App()

    frame = rpcontest_Frame()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    Start()
