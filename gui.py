import plotly
import plotly.graph_objs as go

import os
import sys
import csv
import time
import configparser
import requests

from datetime import date
import datetime

import wx
import wx.html2
import wx.grid
import wx.adv
from wx.lib import masked

import globals

app = wx.App()

class MyFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(1040,600))
		self.CenterOnScreen()
		self.CreateStatusBar()
#		self.SetStatusText("This is the statusbar")

		#Initialising the MenuBar
		menuBar = wx.MenuBar()
		menu1 = wx.Menu()
#		menu1.Append(101,"Paste\tCtrl+V")
#		menu1.Append(102,"Copy\tCtrl+C")
		menu1.AppendSeparator()
		menu1.Append(103,"Quit\tCtrl+Q")
		self.Bind(wx.EVT_MENU, self.MenuClose, id=103)
		menuBar.Append(menu1, "File")
		self.SetMenuBar(menuBar)

		#Initialising the Graphical User Interface (GUI)
		Tabs = wx.Notebook(self, style=wx.BK_BOTTOM)

		panelA = wx.Window(Tabs, wx.ID_ANY)
		Tabs.AddPage(panelA,"Overview")
		browser = wx.html2.WebView.New(panelA)
		browser.LoadURL("file://"+globals.filepath+"/html/"+"overview1.html")

		panelB = wx.Window(panelA, wx.ID_ANY)
		browser2 = wx.html2.WebView.New(panelB)
		browser2.LoadURL("file://"+globals.filepath+"/html/"+"overview2.html")

		panelC = wx.Window(panelB, wx.ID_ANY)
		wx.StaticText(panelC,wx.ID_ANY, "Summary of assets:",(10,10))
		total = 0.0
		total_inv = 0.0
		for i in globals.config.sections():
			fullname = str(globals.config[i]["fullname"])
			j=globals.config.sections().index(i)
			if str(globals.config[i]["type"])=="deka":
				clr=""
				if globals.wealth_amount[j][-1]-globals.invested[j]>0: clr="#00cc00"
				else: clr="red"
				wx.StaticText(panelC,wx.ID_ANY, fullname+" :", (10,(j+1)*40))
				wx.StaticText(panelC,wx.ID_ANY, "", (250,(j+1)*40)).SetLabelMarkup("<b><span color='"+str(globals.config[i]["color"])+"'>"+"{:.2f}".format(globals.wealth_amount[j][-1])+" </span></b>")
				wx.StaticText(panelC,wx.ID_ANY, "", (250-5,(j+1)*40+20)).SetLabelMarkup("<span color='"+str(clr)+"'>"+("+" if globals.wealth_amount[j][-1]-globals.invested[j]>0 else "")+"{:.2f}".format(round(globals.wealth_amount[j][-1]-globals.invested[j],2))+" ("+"{:.2f}".format(round(((globals.wealth_amount[j][-1]-globals.invested[j])/globals.invested[j])*100,2))+" %)</span>")
				total_inv += globals.invested[j]
				total += globals.wealth_amount[j][-1]
			if str(globals.config[i]["type"])=="liq":
				wx.StaticText(panelC,wx.ID_ANY, fullname +" :", (10,(j+1)*40))
				wx.StaticText(panelC,wx.ID_ANY,str(globals.liquidity[0]),(250,(j+1)*40))
		wx.StaticText(panelC,wx.ID_ANY,"Total (w/o Liquidity):", (10,(len(globals.config.sections())+0.5)*40))
		wx.StaticText(panelC,wx.ID_ANY,"",(250,(len(globals.config.sections())+0.5)*40)).SetLabelMarkup("<b>"+str("{:.3f}".format(total))+"</b>")
		wx.StaticText(panelC,wx.ID_ANY,"",(250-5,(len(globals.config.sections())+1.5)*40-20)).SetLabelMarkup("<span color='"+("red" if (total-total_inv)<0 else "#00cc00")+"'>"+("+" if (total-total_inv)>0 else "")+"{:.2f}".format(round(total-total_inv,2))+" ("+"{:.2f}".format(round((total-total_inv)*100/total_inv,2))+" %)"+"</span>")

		bsizer1 = wx.BoxSizer(wx.VERTICAL)
		bsizer1.Add(browser2, 2, wx.EXPAND)
		bsizer1.Add(panelC, 1, wx.EXPAND)
		panelB.SetSizer(bsizer1)

		bsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		bsizer2.Add(browser, 2, wx.EXPAND)
		bsizer2.Add(panelB, 1, wx.EXPAND)
		panelA.SetSizer(bsizer2)

		self.choiceboxes = [] #300+
		self.browsers = []
		self.checkboxes = []
		self.checkboxes_ids = []#400+
		self.checkboxes_auto_ids = []#500+
		self.DatePicker_ids = [] #600+
		self.DatePickers = []
		self.SpinCtrls = []#700+

		self.choices=["Fond Evolution","Investment Evolution"]

		j = 0
		for i in globals.config.sections():
			panelA = wx.Window(Tabs, wx.ID_ANY)
			name = str(globals.config[str(i)]["name"])
			Tabs.AddPage(panelA, name)

			browser = wx.html2.WebView.New(panelA)
			browser.LoadURL("file://"+globals.filepath+"/html/"+name+"/"+name+".html")
			self.browsers.append(browser)

			panelB = wx.Window(panelA, wx.ID_ANY)

			panelC = wx.Window(panelB, wx.ID_ANY)

			t1 = wx.StaticText(panelC,wx.ID_ANY, "Settings")
			choicebox = wx.Choice(panelC, 300+len(self.choiceboxes), choices=self.choices)
			self.choiceboxes.append(choicebox)
			self.Bind(wx.EVT_CHOICE, self.OnChose,choicebox)

			cb = wx.CheckBox(panelC,400+len(self.checkboxes_ids), "Show since establishment")
			self.checkboxes_ids.append(cb.GetId())
			cb.SetValue(False)
			self.checkboxes.append(cb)
			self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, cb)

			if str(globals.config[i]["type"])=="deka":
				clr=""
				if globals.wealth_amount[j][-1]-globals.invested[j]>0: clr="#00cc00"
				else: clr="red"
				wx.StaticText(panelC,wx.ID_ANY,"Invested Amount: ",(10,90))
				wx.StaticText(panelC,wx.ID_ANY,"{:.2f}".format(globals.invested[j]),(250,90))
				wx.StaticText(panelC,wx.ID_ANY,"Value of the Invested Amount\n(w reinvested dividends): ",(10,110))
				wx.StaticText(panelC,wx.ID_ANY,"{:.2f}".format(globals.wealth_amount[j][-1]),(250,115))
				wx.StaticText(panelC,wx.ID_ANY,"Current Holding: ",(10,145))
				wx.StaticText(panelC,wx.ID_ANY,str(round(globals.current_holding[j],3)),(250,145))
				wx.StaticText(panelC,wx.ID_ANY,"",(10,165)).SetLabelMarkup("<span color='blue'>Reinvested dividends:</span>")
				wx.StaticText(panelC,wx.ID_ANY,"{:.2f}".format(globals.dividends_invested[j]),(250,165))
				wx.StaticText(panelC,wx.ID_ANY,"",(10,185)).SetLabelMarkup("<span color='red'>Transferred dividends:</span>")
				wx.StaticText(panelC,wx.ID_ANY,str("{:.2f}".format(globals.dividends_transferred[j])),(250,185))
				wx.StaticText(panelC,wx.ID_ANY,"Total gain/loss:",(10,205))
				wx.StaticText(panelC,wx.ID_ANY,"",(250-5,205)).SetLabelMarkup("<span color='"+str(clr)+"'>"+("+" if globals.wealth_amount[j][-1]-globals.invested[j]>0 else "")+"{:.2f}".format(round(globals.wealth_amount[j][-1]-globals.invested[j],2))+"</span>")
				wx.StaticText(panelC,wx.ID_ANY,"",(250-5,225)).SetLabelMarkup("<span color='"+str(clr)+"'>"+("+" if globals.wealth_amount[j][-1]-globals.invested[j]>0 else "")+"{:.2f}".format(round(((globals.wealth_amount[j][-1]-globals.invested[j])/globals.invested[j])*100,2))+" % </span>")
				cb_aut = wx.CheckBox(panelC,500+len(self.checkboxes_auto_ids),"Monthly Automatisation from:",(10,255))
				self.checkboxes_auto_ids.append(cb_aut.GetId())
				self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBoxAut, cb_aut)
				dpc = wx.adv.DatePickerCtrl(panelC,600+len(self.DatePicker_ids),wx.DateTime.Today(),(10,275))
				if len(globals.wealth_dates[0])>1:
					minimumdate = wx.DateTime(int(str(globals.wealth_dates[j][0])[-2:]),int(str(globals.wealth_dates[j][0])[5:7])-1,int(str(globals.wealth_dates[j][0])[:4]))
					maximumdate = wx.DateTime(int(str(globals.wealth_dates[j][-1])[-2:]),int(str(globals.wealth_dates[j][-1])[5:7])-1,int(str(globals.wealth_dates[j][-1])[:4]))
					dpc.SetRange(minimumdate,maximumdate)
				date = globals.config[i]["aut"]
				if date=="":
					dpc.Disable()
					dpc.SetValue(wx.DateTime.Today())
					cb_aut.SetValue(False)
				else:
					cb_aut.SetValue(True)
					dpc.SetValue(wx.DateTime(int(date[:2]),int(date[3:5])-1,int(date[-4:])))
				self.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChanged, dpc)
				self.DatePicker_ids.append(dpc.GetId())
				self.DatePickers.append(dpc)
				SpinCtrlDouble_amount = wx.SpinCtrlDouble(panelC,value='25.00',min=25, max=1000, pos=(200,280),id=700+len(self.SpinCtrls),inc=0.01)
				if date=="": SpinCtrlDouble_amount.Enable(False)
				if globals.config[i]["aut_amount"]!="": SpinCtrlDouble_amount.SetValue(str(globals.ConvertToFloat(globals.config[i]["aut_amount"])))
				self.SpinCtrls.append(SpinCtrlDouble_amount)
				self.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl, SpinCtrlDouble_amount)
				self.Bind(wx.EVT_TEXT, self.OnSpinCtrl, SpinCtrlDouble_amount)
			if str(globals.config[i]["type"])=="liq":
				wx.StaticText(panelC,wx.ID_ANY,"Available Liqudity",(10,185))
				wx.StaticText(panelC,wx.ID_ANY,str(globals.liquidity[0]),(250,185))
			panelD = wx.Window(panelB,wx.ID_ANY)
			grid = wx.grid.Grid(panelD)
			grid.SetRowLabelSize(0)
			grid.SetMargins(0,0)
			grid.AutoSizeColumns(False)
			name = str(globals.config[str(i)]["name"])
			if str(globals.config[i]["type"])=="deka":
				date_b,amount_b,date_d,amount_d = globals.parseInvestementData(i,name)
				grid.CreateGrid(max(len(date_b),len(amount_b),len(date_d),len(amount_d)),4)
				for k in range(len(date_d)):
					grid.SetCellValue(k,2,date_d[k])
					grid.SetCellValue(k,3,amount_d[k])
					grid.SetCellBackgroundColour(k,2,wx.Colour(0,0,255,80))
					grid.SetCellBackgroundColour(k,3,wx.Colour(0,0,255,80))
				date_d_t, amount_d_t = globals.parseTransferedDividendData(name)
				for k in range(len(date_d_t)):
					index = len(date_d)+k
					grid.SetCellValue(index,2,date_d_t[k])
					grid.SetCellValue(index,3,amount_d_t[k])
					grid.SetCellBackgroundColour(index,2,wx.Colour(255,0,0,80))
					grid.SetCellBackgroundColour(index,3,wx.Colour(255,0,0,80))
				grid.SetColLabelValue(2,"Date \nDividend")
				grid.SetColLabelValue(3,"Amount")
				grid.SetColSize(2,80)
				grid.SetColSize(3,70)
				grid.SetColLabelValue(0,"Date \nBuy")
			if str(globals.config[i]["type"])=="liq":
				date_b,amount_b = globals.parseLiqudityData(name)
				grid.CreateGrid(len(date_b),2)
				cb.Enable(False)
				choicebox.Enable(False)
				grid.SetColLabelValue(0,"Date")
			for k in range(len(date_b)):
				grid.SetCellValue(k,0,date_b[k])
				grid.SetCellValue(k,1,amount_b[k])
			grid.SetColLabelValue(1,"Amount")
			grid.SetColSize(0,80)
			grid.SetColSize(1,70)
			grid.SetRowLabelSize(20)
			grid.EnableEditing(False)
			grid.DisableDragGridSize()

			boxsizerD = wx.BoxSizer(wx.VERTICAL)
			boxsizerD.Add(grid, 0, wx.EXPAND|wx.ALIGN_BOTTOM)
			panelD.SetSizer(boxsizerD)

			boxsizerC = wx.BoxSizer(wx.VERTICAL)
			boxsizerC.Add(t1, 0, wx.ALIGN_TOP|wx.LEFT,10)
			boxsizerC.Add(choicebox, 0, wx.TOP|wx.LEFT, 10)
			boxsizerC.Add(cb, 0, wx.TOP|wx.LEFT, 10)
			panelC.SetSizer(boxsizerC)

			bsizerB = wx.BoxSizer(wx.VERTICAL)
			bsizerB.Add(panelC, 2, wx.EXPAND)
			bsizerB.Add(panelD, 1, wx.EXPAND|wx.FIXED_MINSIZE)
			panelB.SetSizer(bsizerB)

			bsizer1 = wx.BoxSizer(wx.HORIZONTAL)
			bsizer1.Add(browser, 2, wx.EXPAND)
			bsizer1.Add(panelB, 1, wx.EXPAND)
			panelA.SetSizer(bsizer1)
			j+=1

		self.Show(True)

	def MenuClose(self,event):
		self.Close()

	def OnChose(self,event):
#		j = int(str(event.GetId())[-1])
		status = event.GetString()
		for j in range(len(self.checkboxes)):
			name = globals.config[str(globals.config.sections()[j])]["name"]
			self.choiceboxes[j].SetSelection(self.choices.index(status))
			if event.GetString() == self.choices[0]:
				if self.checkboxes[j].GetValue(): self.browsers[j].LoadURL("file://"+globals.filepath+"/html/"+name+"/"+name+"_since_estab.html")
				else: self.browsers[j].LoadURL("file://"+globals.filepath+"/html/"+name+"/"+name+".html")
				self.checkboxes[j].Enable(True)
			else:
				self.browsers[j].LoadURL("file://"+globals.filepath+"/html/"+name+"/"+name+"_inv.html")
				self.checkboxes[j].Enable(False)

	def EvtCheckBox(self,event):
		j = int(str(event.GetId())[-1])
		status = event.IsChecked()
		for j in range(len(self.checkboxes)):
			name = globals.config[str(globals.config.sections()[j])]["name"]
			self.checkboxes[j].SetValue(status)
			cb = event.GetEventObject()
			if cb.GetValue():self.browsers[j].LoadURL("file://"+globals.filepath+"/html/"+name+"/"+name+"_since_estab.html")
			else: self.browsers[j].LoadURL("file://"+globals.filepath+"/html/"+name+"/"+name+".html")

	def EvtCheckBoxAut(self,event):
		j = int(str(event.GetId())[-1])
		self.DatePickers[j].Enable(event.IsChecked())
		self.SpinCtrls[j].Enable(event.IsChecked())
		if event.IsChecked():
			value = self.DatePickers[j].GetValue()
			globals.config[globals.config.sections()[j]]["aut"] = ("0" if len(str(value.day))==1 else "")+str(value.day)+"."+("0" if len(str(int(value.month)+1))==1 else "")+str(int(value.month)+1)+"."+str(value.year)
			globals.config[globals.config.sections()[j]]["aut_amount"] = ConvertAmountToWritable(self.SpinCtrls[j].GetValue())
		else:
			globals.config[globals.config.sections()[j]]["aut"] = ""
			globals.config[globals.config.sections()[j]]["aut_amount"] = ""
			self.SpinCtrls[j].SetValue("25.00")
		globals.config.write(open("globals.config.conf","w"))

	def OnDateChanged(self,event):
		j = int(str(event.GetId())[-1])
		value = self.DatePickers[j].GetValue()
		globals.config[globals.config.sections()[j]]["aut"] = ("0" if len(str(value.day))==1 else "")+str(value.day)+"."+("0" if len(str(int(value.month)+1))==1 else "")+str(int(value.month)+1)+"."+str(value.year)
		globals.config.write(open("globals.config.conf","w"))

	def OnSpinCtrl(self, event):
		j = int(str(event.GetId())[-1])
		value = self.SpinCtrls[j].GetValue()
		globals.config[globals.config.sections()[j]]["aut_amount"] = ConvertAmountToWritable(value)
		globals.config.write(open("globals.config.conf","w"))

def plotOverviewGraphs():
	globals.print_if_allowed("Making Summary plots...")
	(dates_unified, amount_unified) = globals.unifyData()
	data = []
	stack_levels = []
	pie_values = []
	pie_labels = []
	chart_colors = []
	for i in range(len(globals.config.sections())):
		stack_levels.append(int(globals.config[str(globals.config.sections()[i])]["stack"]))
	for i in range(len(stack_levels)):
		if i==0: continue #liquidity
		index = stack_levels.index(i)
		name = str(globals.config[str(globals.config.sections()[index])]["name"])
		chart_colors.append(str(globals.config[str(globals.config.sections()[index])]["color"]))
		trace = go.Scatter(x=dates_unified,y=amount_unified[index],fill='tonexty',stackgroup='one', name=name,line=dict(color=chart_colors[-1]))
		data.append(trace)

		pie_labels.append(name)
		pie_values.append(amount_unified[index][-1])

	layout = dict(title="Overview of total assets")
	fig = dict(data=data,layout=layout)
	if not globals.mode_only_state: plotly.offline.plot(fig, filename="html/overview1.html", auto_open=False)

	layout = dict(
				autosize=True,
				margin=go.layout.Margin(l=0,r=0,b=0,t=0,pad=1),
			)
	trace = go.Pie(labels=pie_labels, values=pie_values, showlegend=False, marker=dict(colors=chart_colors),textinfo='percent')
	fig = dict(data=[trace], layout=layout)
	if not globals.mode_only_state: plotly.offline.plot(fig,filename="html/overview2.html", auto_open=False)

def plot():
	globals.print_if_allowed("Making",len(globals.config.sections()),"plots...")
	for i in range(len(globals.config.sections())):
		name = str(globals.config[str(globals.config.sections()[i])]["name"])
		fullname = str(globals.config[str(globals.config.sections()[i])]["fullname"])
		if(os.path.isdir(os.path.dirname(os.path.abspath(__file__))+"/html/"))==False:
			os.mkdir(os.path.dirname(os.path.abspath(__file__))+"/html/")
		if(os.path.isdir(os.path.dirname(os.path.abspath(__file__))+"/html/"+name))==False:
			os.mkdir(os.path.dirname(os.path.abspath(__file__))+"/html/"+name)
		globals.print_if_allowed("Creating Graphs for", fullname+str("..."))
		if str(globals.config[str(globals.config.sections()[i])]["type"])=="deka":
			x,y1,y2 = globals.parseDekaData(i, name)
			date_b,amount_b,date_d,amount_d = globals.parseInvestementData(globals.config.sections()[i],name,AsDate=True)
			fill_color = str(globals.config[str(globals.config.sections()[i])]["color"])
			layout = dict(
				title=fullname,
				xaxis=dict(
					rangeselector=dict(
						buttons=list([
							dict(count=1,
								 label='1m',
								 step='month',
								 stepmode='backward'),
							dict(count=6,
								 label='6m',
								 step='month',
								 stepmode='backward'),
							dict(count=1,
								 label='1y',
								 step='year',
								 stepmode='backward'),
							dict(count=3,
								 label='3y',
								 step='year',
								 stepmode='backward'),
							dict(count=5,
								 label='5y',
								 step='year',
								 stepmode='backward'),
							dict(step='all')
						])
					),
					rangeslider=dict(
						visible = True
					),
					type='date'
				)
			)
			data1 = go.Scatter(
				x=x,
				y=y1,
				name = "Price (Buy)",
				line=dict(color='#7f7f7f'))
			data2 = go.Scatter(
				x=x,
				y=y2,
				name = "Price (Sell)",
				line=(dict(color = fill_color)))
			fig = dict(data=[data1, data2], layout=layout)
			plotly.offline.plot(fig,filename=("html/"+name+"/"+name+"_since_estab.html"), auto_open=False)

			data3 = go.Scatter(
				x=globals.wealth_dates[i],
				y=globals.wealth_amount[i],
				name = "Investment (w div)",
				line=(dict(color = fill_color)),
				fill='tozeroy')
			data4 = go.Scatter(
				x=globals.wealth_dates[i],
				y=globals.invested_all[i],
				name = "Invested amount (w/o div)",
				line=dict(color='#7f7f7f'))
			fig = dict(data=[data3,data4], layout=layout)
			plotly.offline.plot(fig,filename=("html/"+name+"/"+name+"_inv.html"), auto_open=False)

			data1 = go.Scatter(
				x=globals.wealth_dates[i],
				y=y1[x.index(date_b[-1]):],
				name = "Price (Buy)",
				line=dict(color='#7f7f7f'))
			data2 = go.Scatter(
				x=globals.wealth_dates[i],
				y=y2[x.index(date_b[-1]):],
				name = "Price (Sell)",
				line=(dict(color = fill_color)))
			fig = dict(data=[data1, data2], layout=layout)
			plotly.offline.plot(fig,filename=("html/"+name+"/"+name+".html"), auto_open=False)

		else:
			x,y = globals.parseLiqudityData(name, AsDate=True, AsFloat=True)
			layout = dict(
				title=fullname,
				xaxis=dict(
					rangeselector=dict(
						buttons=list([
							dict(count=1,
								 label='1m',
								 step='month',
								 stepmode='backward'),
							dict(count=6,
								 label='6m',
								 step='month',
								 stepmode='backward'),
							dict(count=1,
								 label='1y',
								 step='year',
								 stepmode='backward'),
							dict(count=3,
								 label='3y',
								 step='year',
								 stepmode='backward'),
							dict(count=5,
								 label='5y',
								 step='year',
								 stepmode='backward'),
							dict(step='all')
						])
					),
					rangeslider=dict(
						visible = True
					),
					type='date'
				)
			)
			data1 = go.Scatter(
				x=x,
				y=y,
				name = "Liquidity",
#				opacity = 0.8,
				fill='tozeroy')
			fig = dict(data=[data1], layout=layout)
			plotly.offline.plot(fig,filename=("html/"+name+"/"+name+".html"), auto_open=False)

def gui_init(title="Online Mode"):
	if title == "Online Mode":
		plot()
		plotOverviewGraphs()
	Frame = MyFrame(None, title)

def gui_main_loop():
	app.MainLoop()
