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

config = configparser.ConfigParser()
filepath = os.path.dirname(os.path.abspath(__file__))
config.read(filepath+"/config.conf")
wealth_dates = []
wealth_amount = []
invested = []
invested_all = []
dividends_invested = []
dividends_transferred = []
liquidity = []
current_holding = []

#Argument settings
printing_allowed = False
mode_only_state = False
mode_CLI = False
mode_history_days = -999

#Error printouts:
error_connection_deka_server = []

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
		browser.LoadURL("file://"+filepath+"/html/"+"overview1.html")

		panelB = wx.Window(panelA, wx.ID_ANY)
		browser2 = wx.html2.WebView.New(panelB)
		browser2.LoadURL("file://"+filepath+"/html/"+"overview2.html")

		panelC = wx.Window(panelB, wx.ID_ANY)
		wx.StaticText(panelC,wx.ID_ANY, "Summary of assets:",(10,10))
		total = 0.0
		total_inv = 0.0
		for i in config.sections():
			fullname = str(config[i]["fullname"])
			j=config.sections().index(i)
			if str(config[i]["type"])=="deka":
				clr=""
				if wealth_amount[j][-1]-invested[j]>0: clr="#00cc00"
				else: clr="red"
				wx.StaticText(panelC,wx.ID_ANY, fullname+" :", (10,(j+1)*40))
				wx.StaticText(panelC,wx.ID_ANY, "", (250,(j+1)*40)).SetLabelMarkup("<b><span color='"+str(config[i]["color"])+"'>"+"{:.2f}".format(wealth_amount[j][-1])+" </span></b>")
				wx.StaticText(panelC,wx.ID_ANY, "", (250-5,(j+1)*40+20)).SetLabelMarkup("<span color='"+str(clr)+"'>"+("+" if wealth_amount[j][-1]-invested[j]>0 else "")+"{:.2f}".format(round(wealth_amount[j][-1]-invested[j],2))+" ("+"{:.2f}".format(round(((wealth_amount[j][-1]-invested[j])/invested[j])*100,2))+" %)</span>")
				total_inv += invested[j]
				total += wealth_amount[j][-1]
			if str(config[i]["type"])=="liq":
				wx.StaticText(panelC,wx.ID_ANY, fullname +" :", (10,(j+1)*40))
				wx.StaticText(panelC,wx.ID_ANY,str(liquidity[0]),(250,(j+1)*40))
		wx.StaticText(panelC,wx.ID_ANY,"Total (w/o Liquidity):", (10,(len(config.sections())+0.5)*40))
		wx.StaticText(panelC,wx.ID_ANY,"",(250,(len(config.sections())+0.5)*40)).SetLabelMarkup("<b>"+str("{:.3f}".format(total))+"</b>")
		wx.StaticText(panelC,wx.ID_ANY,"",(250-5,(len(config.sections())+1.5)*40-20)).SetLabelMarkup("<span color='"+("red" if (total-total_inv)<0 else "#00cc00")+"'>"+("+" if (total-total_inv)>0 else "")+"{:.2f}".format(round(total-total_inv,2))+" ("+"{:.2f}".format(round((total-total_inv)*100/total_inv,2))+" %)"+"</span>")

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
		for i in config.sections():
			panelA = wx.Window(Tabs, wx.ID_ANY)
			name = str(config[str(i)]["name"])
			Tabs.AddPage(panelA, name)

			browser = wx.html2.WebView.New(panelA)
			browser.LoadURL("file://"+filepath+"/html/"+name+"/"+name+".html")
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

			if str(config[i]["type"])=="deka":
				clr=""
				if wealth_amount[j][-1]-invested[j]>0: clr="#00cc00"
				else: clr="red"
				wx.StaticText(panelC,wx.ID_ANY,"Invested Amount: ",(10,90))
				wx.StaticText(panelC,wx.ID_ANY,"{:.2f}".format(invested[j]),(250,90))
				wx.StaticText(panelC,wx.ID_ANY,"Value of the Invested Amount\n(w reinvested dividends): ",(10,110))
				wx.StaticText(panelC,wx.ID_ANY,"{:.2f}".format(wealth_amount[j][-1]),(250,115))
				wx.StaticText(panelC,wx.ID_ANY,"Current Holding: ",(10,145))
				wx.StaticText(panelC,wx.ID_ANY,str(round(current_holding[j],3)),(250,145))
				wx.StaticText(panelC,wx.ID_ANY,"",(10,165)).SetLabelMarkup("<span color='blue'>Reinvested dividends:</span>")
				wx.StaticText(panelC,wx.ID_ANY,"{:.2f}".format(dividends_invested[j]),(250,165))
				wx.StaticText(panelC,wx.ID_ANY,"",(10,185)).SetLabelMarkup("<span color='red'>Transferred dividends:</span>")
				wx.StaticText(panelC,wx.ID_ANY,str("{:.2f}".format(dividends_transferred[j])),(250,185))
				wx.StaticText(panelC,wx.ID_ANY,"Total gain/loss:",(10,205))
				wx.StaticText(panelC,wx.ID_ANY,"",(250-5,205)).SetLabelMarkup("<span color='"+str(clr)+"'>"+("+" if wealth_amount[j][-1]-invested[j]>0 else "")+"{:.2f}".format(round(wealth_amount[j][-1]-invested[j],2))+"</span>")
				wx.StaticText(panelC,wx.ID_ANY,"",(250-5,225)).SetLabelMarkup("<span color='"+str(clr)+"'>"+("+" if wealth_amount[j][-1]-invested[j]>0 else "")+"{:.2f}".format(round(((wealth_amount[j][-1]-invested[j])/invested[j])*100,2))+" % </span>")
				cb_aut = wx.CheckBox(panelC,500+len(self.checkboxes_auto_ids),"Monthly Automatisation from:",(10,255))
				self.checkboxes_auto_ids.append(cb_aut.GetId())
				self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBoxAut, cb_aut)
				dpc = wx.adv.DatePickerCtrl(panelC,600+len(self.DatePicker_ids),wx.DateTime.Today(),(10,275))
				if len(wealth_dates[0])>1:
					minimumdate = wx.DateTime(int(str(wealth_dates[j][0])[-2:]),int(str(wealth_dates[j][0])[5:7])-1,int(str(wealth_dates[j][0])[:4]))
					maximumdate = wx.DateTime(int(str(wealth_dates[j][-1])[-2:]),int(str(wealth_dates[j][-1])[5:7])-1,int(str(wealth_dates[j][-1])[:4]))
					dpc.SetRange(minimumdate,maximumdate)
				date = config[i]["aut"]
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
				if config[i]["aut_amount"]!="": SpinCtrlDouble_amount.SetValue(str(ConvertToFloat(config[i]["aut_amount"])))
				self.SpinCtrls.append(SpinCtrlDouble_amount)
				self.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl, SpinCtrlDouble_amount)
				self.Bind(wx.EVT_TEXT, self.OnSpinCtrl, SpinCtrlDouble_amount)
			if str(config[i]["type"])=="liq":
				wx.StaticText(panelC,wx.ID_ANY,"Available Liqudity",(10,185))
				wx.StaticText(panelC,wx.ID_ANY,str(liquidity[0]),(250,185))
			panelD = wx.Window(panelB,wx.ID_ANY)
			grid = wx.grid.Grid(panelD)
			grid.SetRowLabelSize(0)
			grid.SetMargins(0,0)
			grid.AutoSizeColumns(False)
			name = str(config[str(i)]["name"])
			if str(config[i]["type"])=="deka":
				date_b,amount_b,date_d,amount_d = parseInvestementData(i,name)
				grid.CreateGrid(max(len(date_b),len(amount_b),len(date_d),len(amount_d)),4)
				for k in range(len(date_d)):
					grid.SetCellValue(k,2,date_d[k])
					grid.SetCellValue(k,3,amount_d[k])
					grid.SetCellBackgroundColour(k,2,wx.Colour(0,0,255,80))
					grid.SetCellBackgroundColour(k,3,wx.Colour(0,0,255,80))
				date_d_t, amount_d_t = parseTransferedDividendData(name)
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
			if str(config[i]["type"])=="liq":
				date_b,amount_b = parseLiqudityData(name)
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
			name = config[str(config.sections()[j])]["name"]
			self.choiceboxes[j].SetSelection(self.choices.index(status))
			if event.GetString() == self.choices[0]:
				if self.checkboxes[j].GetValue(): self.browsers[j].LoadURL("file://"+filepath+"/html/"+name+"/"+name+"_since_estab.html")
				else: self.browsers[j].LoadURL("file://"+filepath+"/html/"+name+"/"+name+".html")
				self.checkboxes[j].Enable(True)
			else:
				self.browsers[j].LoadURL("file://"+filepath+"/html/"+name+"/"+name+"_inv.html")
				self.checkboxes[j].Enable(False)

	def EvtCheckBox(self,event):
		j = int(str(event.GetId())[-1])
		status = event.IsChecked()
		for j in range(len(self.checkboxes)):
			name = config[str(config.sections()[j])]["name"]
			self.checkboxes[j].SetValue(status)
			cb = event.GetEventObject()
			if cb.GetValue():self.browsers[j].LoadURL("file://"+filepath+"/html/"+name+"/"+name+"_since_estab.html")
			else: self.browsers[j].LoadURL("file://"+filepath+"/html/"+name+"/"+name+".html")

	def EvtCheckBoxAut(self,event):
		j = int(str(event.GetId())[-1])
		self.DatePickers[j].Enable(event.IsChecked())
		self.SpinCtrls[j].Enable(event.IsChecked())
		if event.IsChecked():
			value = self.DatePickers[j].GetValue()
			config[config.sections()[j]]["aut"] = ("0" if len(str(value.day))==1 else "")+str(value.day)+"."+("0" if len(str(int(value.month)+1))==1 else "")+str(int(value.month)+1)+"."+str(value.year)
			config[config.sections()[j]]["aut_amount"] = ConvertAmountToWritable(self.SpinCtrls[j].GetValue())
		else:
			config[config.sections()[j]]["aut"] = ""
			config[config.sections()[j]]["aut_amount"] = ""
			self.SpinCtrls[j].SetValue("25.00")
		config.write(open("config.conf","w"))

	def OnDateChanged(self,event):
		j = int(str(event.GetId())[-1])
		value = self.DatePickers[j].GetValue()
		config[config.sections()[j]]["aut"] = ("0" if len(str(value.day))==1 else "")+str(value.day)+"."+("0" if len(str(int(value.month)+1))==1 else "")+str(int(value.month)+1)+"."+str(value.year)
		config.write(open("config.conf","w"))

	def OnSpinCtrl(self, event):
		j = int(str(event.GetId())[-1])
		value = self.SpinCtrls[j].GetValue()
		config[config.sections()[j]]["aut_amount"] = ConvertAmountToWritable(value)
		config.write(open("config.conf","w"))


def ConvertToFloat(x):
	r = ""
	for i in range(len(x)):
		if x[i]=="." :
			r+=""
			continue
		if x[i]=="," :
			r+="."
			continue
		r+=x[i]
	return float(r)

def ConvertAmountToWritable(x):
	s = str(x)
	i = s.index(".")
	pre = int(s[:i])
	post = int(s[i+1:])
	return str(pre)+","+(str(post) if len(str(post))==2 else "0"+str(post))


def ConvertDateToGerman(x):
	r = ""
	r+=str(x.day) if len(str(x.day))==2 else "0"+str(x.day)
	r+="."
	r+=str(x.month) if len(str(x.month))==2 else "0"+str(x.month)
	r+="."
	r+=str(x.year)
	return r

def writeNewCSVData(i,name,new_date_b,new_amount_b):
	with open("csv/"+name+"/"+name+"_inv.csv", mode='w') as csvfile:
		writer = csv.writer(csvfile,delimiter=";")
		writer.writerow(["Date","Amount",""])
		for j in range(len(new_date_b)):
			writer.writerow([ConvertDateToGerman(new_date_b[j]),new_amount_b[j]])

def checkMonthlyAutomatisation(i,name):
	deka_date = []
	deka_price = []
	filename = "csv/"+name+"/"+name+".csv"
	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=";")
		for row in reader:
			deka_date.append(date(int(row['Datum'][-4:]),int(row['Datum'][3:5]),int(row['Datum'][:2])))
			deka_price.append(ConvertToFloat(row['Ausgabepreis']))

	date_b,amount_b = [],[]
	with open("csv/"+name+"/"+name+"_inv.csv") as csvfile:
		reader = csv.DictReader(csvfile, delimiter=";")
		for row in reader:
			date_b.append(date(int(row['Date'][-4:]),int(row['Date'][3:5]),int(row['Date'][:2])))
			amount_b.append(str(row['Amount']))
	monthly_autom = config[i]["aut"]
	if monthly_autom !="":
		monthly_d_0 = date(int(monthly_autom[-4:]),int(monthly_autom[3:5]),int(monthly_autom[:2]))
		monthly_d_ref = monthly_d_0
		j=0
		k=0
		while (monthly_d_ref-datetime.date.today()).days<=0:
			datebuy = date_b[0]
			for d in deka_date:
				timedelta = d-monthly_d_ref
				if timedelta.days >= 0:
					datebuy=d
					break
			if datebuy not in date_b:
				print_if_allowed("bought of",name,"on",datebuy,"for",config[i]["aut_amount"])
				date_b = [datebuy]+date_b
				amount_b = [str(config[i]["aut_amount"])]+amount_b
				writeNewCSVData(i,name,date_b,amount_b)

			j+=1
			if (int(monthly_autom[3:5])+j)%12==1:
				k+=1
			if (int(monthly_autom[3:5])+j)%12==0:
				monthly_d_ref = date(int(monthly_autom[-4:])+k,12,int(monthly_autom[:2]))
			else: monthly_d_ref = date(int(monthly_autom[-4:])+k,(int(monthly_autom[3:5])+j)%12,int(monthly_autom[:2]))


def parseInvestementData(i, name, AsDate=False):
	checkMonthlyAutomatisation(i, name)
	date_b,amount_b,date_d,amount_d = [],[],[],[]
	with open("csv/"+name+"/"+name+"_inv.csv") as csvfile:
		reader = csv.DictReader(csvfile, delimiter=";")
		for row in reader:
			if AsDate: date_b.append(str(date(int(row['Date'][-4:]),int(row['Date'][3:5]),int(row['Date'][:2]))))
			else: date_b.append(str(row['Date'][:2])+"."+str(row['Date'][3:5])+"."+str(row['Date'][-4:]))#y,m,d
			amount_b.append(str(row['Amount']))
	with open("csv/"+name+"/"+name+"_div.csv") as csvfile:
		reader = csv.DictReader(csvfile, delimiter=";")
		for row in reader:
			if AsDate: date_d.append(str(date(int(row['Date'][-4:]),int(row['Date'][3:5]),int(row['Date'][:2]))))
			else: date_d.append(str(row['Date'][:2])+"."+str(row['Date'][3:5])+"."+str(row['Date'][-4:]))#y,m,d
			amount_d.append(str(row['Amount']))
	return date_b,amount_b,date_d,amount_d

def parseTransferedDividendData(name,AsDate=False, AsFloat=False):
	date_d,amount_d = [],[]
	try:
		with open("csv/"+name+"/"+name+"_div_trans.csv") as csvfile:
			reader = csv.DictReader(csvfile, delimiter=";")
			for row in reader:
				if AsDate: date_d.append(str(date(int(row['Date'][-4:]),int(row['Date'][3:5]),int(row['Date'][:2]))))
				else: date_d.append(str(row['Date'][:2])+"."+str(row['Date'][3:5])+"."+str(row['Date'][-4:]))#y,m,d
				if AsFloat: amount_d.append(ConvertToFloat(str(row['Amount'])))
				else: amount_d.append(str(row['Amount']))
	except FileNotFoundError:
		date_d,amount_d = [],[]
	return date_d,amount_d


def parseLiqudityData(name,AsDate=False, AsFloat=False):
	date_b,amount_b = [],[]
	with open("csv/"+name+"/"+name+".csv") as csvfile:
		reader = csv.DictReader(csvfile, delimiter=";")
		for row in reader:
			if AsDate: date_b.append(str(date(int(row['Date'][-4:]),int(row['Date'][3:5]),int(row['Date'][:2]))))
			else: date_b.append(str(row['Date'][:2])+"."+str(row['Date'][3:5])+"."+str(row['Date'][-4:]))#y,m,d
			if AsFloat: amount_b.append(ConvertToFloat(str(row['Amount'])))
			else: amount_b.append(str(row['Amount']))
	return date_b,amount_b

def updateDekaData(i, name):
	ISIN = str(config[str(config.sections()[i])]["isin"])
	url = "https://www.deka.de/site/dekade_privatkunden_site/wertentwicklung/3966944/index.html?assetcategory=10&produktkennungswert=null&isin="+ISIN+"&action=exportcsv&exporttype=preisentwicklung&gebuehrenBeruecksichtigen=true&von=0&bis="+str(int(time.time()))+"000"
	try:
		r = requests.get(url)
		if(os.path.isdir(os.path.dirname(os.path.abspath(__file__))+"/csv/"))==False:
			os.mkdir(os.path.dirname(os.path.abspath(__file__))+"/csv/")
		if(os.path.isdir(os.path.dirname(os.path.abspath(__file__))+"/csv/"+name))==False:
			os.mkdir(os.path.dirname(os.path.abspath(__file__))+"/csv/"+name)
		filename = "csv/"+name+"/"+name+".csv"
		file = open(filename,"w+")
		file.write(r.text)
		file.close()
	except requests.exceptions.ConnectionError:
		error_connection_deka_server.append(("Connection error... Updating database for "+name+" failed"))

def parseDekaData(i, name, update=False):
	x,y1,y2 = [],[],[]
	if update: updateDekaData(i, name)
	filename = "csv/"+name+"/"+name+".csv"
	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=";")
		try:
			for row in reader:
				x.append(str(date(int(row['Datum'][-4:]),int(row['Datum'][3:5]),int(row['Datum'][:2]))))
				y1.append(ConvertToFloat(row['Ausgabepreis']))
				y2.append(ConvertToFloat(row['Anteilpreis']))
		except KeyError:
			return parseDekaData(i,name, True) #This means the Deka server has returned nonsense... Hit it again
	return x,y1,y2

def unifyData():
	dates_unified, amount_unified = [],[]
	for i in range(len(wealth_amount)):
		amount_unified.append([])
	for i in range(len(wealth_dates)):
		for dates in wealth_dates[i]:
			if dates not in dates_unified:
				dates_unified.append(dates)
	#sorting:
	dates_unified = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in dates_unified]
	dates_unified.sort()
	dates_unified = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates_unified]
	for dates in dates_unified:
		for i in range(len(wealth_amount)):
			if dates in wealth_dates[i]:
				index = wealth_dates[i].index(dates)
				amount_unified[i].append(wealth_amount[i][index])
			else:
				if len(amount_unified[i])==0: amount_unified[i].append(0.0)
				else: amount_unified[i].append(amount_unified[i][-1])
	return dates_unified, amount_unified

def readIn_and_update_Data():
	if printing_allowed==True or mode_CLI==True:
		percent = float(0) / len(config.sections())
		arrow = '-' * int(round(percent * 50)-1) + '>'
		spaces = ' ' * (50 - len(arrow))
		sys.stdout.write("\rFetching Data...: [\033[47;m{0}] {1}%".format(arrow +"\033[0m" + spaces, int(round(percent * 100))))
		sys.stdout.flush()
	for i in range(len(config.sections())):
		name = str(config[str(config.sections()[i])]["name"])
		if str(config[str(config.sections()[i])]["type"])=="deka":
			x,y1,y2 = parseDekaData(i, name, True)
			date_b,amount_b,date_d,amount_d = parseInvestementData(config.sections()[i],name,AsDate=True)
			dates_from_day_1 = x[x.index(date_b[-1]):]
			
			pcs_at_t = 0.0
			values = []
			investment = []
			inv = 0.0
			k1=len(date_b)-1
			k2=len(date_d)-1
			for j in range(len(dates_from_day_1)):
				index = x.index(dates_from_day_1[j])
				if k1>-1:
					if dates_from_day_1[j]==date_b[k1]:
						pcs_at_t+=round(ConvertToFloat(amount_b[k1])*(float(y2[index])/float(y1[index])) /float(y2[index]),3)
						inv+=ConvertToFloat(amount_b[k1])
						k1-=1
				if k2>-1:
					if dates_from_day_1[j]==date_d[k2]:
						pcs_at_t+=round(ConvertToFloat(amount_d[k2])/y2[index],3)
						k2-=1
				values.append(round(pcs_at_t*y2[index],2))
				investment.append(inv)
			current_holding.append(pcs_at_t)
			wealth_dates.append(dates_from_day_1)
			wealth_amount.append(values)
			invested.append(investment[-1])
			invested_all.append(investment)
			d_inv = 0.0
			for s in amount_d: d_inv+=ConvertToFloat(s)
			dividends_invested.append(d_inv)
			dividends_transferred_dates,dividends_transferred_amounts = parseTransferedDividendData(name, AsFloat=True)
			dividends_transferred.append(sum(dividends_transferred_amounts))
		else:
			x,y = parseLiqudityData(name, AsDate=True, AsFloat=True)
			wealth_dates.append(x)
			wealth_amount.append(y)
			liquidity.append(y[0])
		#updating the status bar...
		if printing_allowed==True or mode_CLI==True:
			percent = float(i+1) / len(config.sections())
			arrow = '-' * int(round(percent * 50)-1) + '>'
			spaces = ' ' * (50 - len(arrow))
			sys.stdout.write("\rFetching Data...: [\033[47;m{0}] {1}%".format(arrow + "\033[0m" + spaces, int(round(percent * 100))))
			sys.stdout.flush()
		if i==max(range(len(config.sections()))):
			print("") #ensuring new printouts are written in new lines...
			for s in error_connection_deka_server:
				print(s)



def plotOverviewGraphs():
	print_if_allowed("Making Summary plots...")
	(dates_unified, amount_unified) = unifyData()
	data = []
	stack_levels = []
	pie_values = []
	pie_labels = []
	chart_colors = []
	for i in range(len(config.sections())):
		stack_levels.append(int(config[str(config.sections()[i])]["stack"]))
	for i in range(len(stack_levels)):
		if i==0: continue #liquidity
		index = stack_levels.index(i)
		name = str(config[str(config.sections()[index])]["name"])
		chart_colors.append(str(config[str(config.sections()[index])]["color"]))
		trace = go.Scatter(x=dates_unified,y=amount_unified[index],fill='tonexty',stackgroup='one', name=name,line=dict(color=chart_colors[-1]))
		data.append(trace)

		pie_labels.append(name)
		pie_values.append(amount_unified[index][-1])

	layout = dict(title="Overview of total assets")
	fig = dict(data=data,layout=layout)
	if not mode_only_state: plotly.offline.plot(fig, filename="html/overview1.html", auto_open=False)

	layout = dict(
				autosize=True,
				margin=go.layout.Margin(l=0,r=0,b=0,t=0,pad=1),
			)
	trace = go.Pie(labels=pie_labels, values=pie_values, showlegend=False, marker=dict(colors=chart_colors),textinfo='percent')
	fig = dict(data=[trace], layout=layout)
	if not mode_only_state: plotly.offline.plot(fig,filename="html/overview2.html", auto_open=False)

def plot():
	print_if_allowed("Making",len(config.sections()),"plots...")
	for i in range(len(config.sections())):
		name = str(config[str(config.sections()[i])]["name"])
		fullname = str(config[str(config.sections()[i])]["fullname"])
		if(os.path.isdir(os.path.dirname(os.path.abspath(__file__))+"/html/"))==False:
			os.mkdir(os.path.dirname(os.path.abspath(__file__))+"/html/")
		if(os.path.isdir(os.path.dirname(os.path.abspath(__file__))+"/html/"+name))==False:
			os.mkdir(os.path.dirname(os.path.abspath(__file__))+"/html/"+name)
		print_if_allowed("Creating Graphs for", fullname+str("..."))
		if str(config[str(config.sections()[i])]["type"])=="deka":
			x,y1,y2 = parseDekaData(i, name)
			date_b,amount_b,date_d,amount_d = parseInvestementData(config.sections()[i],name,AsDate=True)
			fill_color = str(config[str(config.sections()[i])]["color"])
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
				x=wealth_dates[i],
				y=wealth_amount[i],
				name = "Investment (w div)",
				line=(dict(color = fill_color)),
				fill='tozeroy')
			data4 = go.Scatter(
				x=wealth_dates[i],
				y=invested_all[i],
				name = "Invested amount (w/o div)",
				line=dict(color='#7f7f7f'))
			fig = dict(data=[data3,data4], layout=layout)
			plotly.offline.plot(fig,filename=("html/"+name+"/"+name+"_inv.html"), auto_open=False)

			data1 = go.Scatter(
				x=wealth_dates[i],
				y=y1[x.index(date_b[-1]):],
				name = "Price (Buy)",
				line=dict(color='#7f7f7f'))
			data2 = go.Scatter(
				x=wealth_dates[i],
				y=y2[x.index(date_b[-1]):],
				name = "Price (Sell)",
				line=(dict(color = fill_color)))
			fig = dict(data=[data1, data2], layout=layout)
			plotly.offline.plot(fig,filename=("html/"+name+"/"+name+".html"), auto_open=False)

		else:
			x,y = parseLiqudityData(name, AsDate=True, AsFloat=True)
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

def print_if_allowed(*string):
	if printing_allowed: print(*string)

bash_mode_arrows = {"True":"\033[32m\uf55b\033[37m","False":"\033[31m\uf542\033[37m"} #up, down
bash_mode_arrows_bold = {"True":"\033[32m\uf062\033[37m","False":"\033[31m\uf063\033[37m"} #up, down

if __name__ == '__main__':
	args = sys.argv
	if ("--help" in args) or ("-h") in args:
		print("DekaPlotter")
		print("  Arguments:")
		print("{:4} {:25} - {}".format("","--msg, --msgs or -m","Shows startup progress"))
		print("{:4} {:25} - {}".format("","--status, --state or -s","Shows data only in terminal"))
		print("{:4} {:25} - {}".format("","--hist n", "Shows investement history of the past n (def: 10) days"))

	else:
		if ("--msg" in args) or ("--msgs" in args) or ("-m" in args): printing_allowed = True
		if ("--status" in args) or ("--state" in args) or ("-s" in args):
			mode_only_state = True
			mode_CLI = True
		if "--hist" in args:
			mode_CLI = True
			if args.index("--hist")+1<len(args):
				try:
					mode_history_days = int(args[args.index("--hist")+1])
				except ValueError:
					if args[args.index("--hist")+1][0]!="-": print("Warning: could not convert",args[args.index("--hist")+1],"to int; default: 10")
					mode_history_days = 10
				if mode_history_days <= 0:
					print("Warning: ",mode_history_days,"is smaller then 0; returning to default: 10")
					mode_history_days = 10
			else:
				mode_history_days = 10
		print_if_allowed("Welcome!")
		readIn_and_update_Data()
		try:
			if not mode_CLI:
				app = wx.App()
				plot()
				plotOverviewGraphs()
				Frame = MyFrame(None, "Online Mode")
		except requests.exceptions.ConnectionError:
			print_if_allowed("Connection Error, starting in offline mode...")
			"""for i in config.sections():
				wealth_dates.append([0])
				wealth_amount.append([0])
				invested.append(1)
				dividends_invested.append([0])
				dividends_transferred.append([0])
				current_holding.append(0)
				liquidity.append(0)
			"""
			if not mode_CLI: Frame = MyFrame(None, "Offline Mode")
		if not mode_CLI:
			print_if_allowed("Starting Application...")
			app.MainLoop()
		else:
			if mode_only_state:
				topbar = "{:35}: {:7} ({:7}) ({:>7}) [{:7}] {:8}".format("Product name", "Value", "Gain/Loss","Real G/L","C.Hold.","Hist(5d)")
				print("="*(len(topbar)+1))
				print(topbar)
				print("-"*(len(topbar)+1))
				total = 0.0
				total_inv = 0.0
				total_5dhistory = 6*[0] #6-days ago;5 days ago;...;today
				for i in range(len(wealth_amount)):
					inv_type = str(config[str(config.sections()[i])]["type"])
					fullname = str(config[str(config.sections()[i])]["fullname"])
					wealth = wealth_amount[i][-1]
					if inv_type=="deka":
						total += wealth
						total_inv += invested[i]
						diff_in_percent = ((wealth_amount[i][-1]-invested[i])/invested[i])*100
						diff_in_percent = ("+" if diff_in_percent>0 else "")+"{:.2f}".format(diff_in_percent)
						diff = (wealth_amount[i][-1]-invested[i])
						diff = ("+" if diff>0 else "")+"{:.2f}".format(diff)
						history = ""
						for j in range(6):
							total_5dhistory[5-j] += wealth_amount[i][-1-j]
							if j!=5:
								history = bash_mode_arrows[str(wealth_amount[i][-1-j]>wealth_amount[i][-2-j])]+history
								if wealth_amount[i][-1-j]==wealth_amount[i][-2-j]: history = "\033[33m\uf553\033[37m"+history[len(bash_mode_arrows[str(wealth_amount[i][-1-j]>wealth_amount[i][-2-j])]):]
						history += " "+bash_mode_arrows_bold[str(wealth_amount[i][-1]>wealth_amount[i][-6])]
						print(("{:35}: {:7.2f} ("+("\033[32m" if (wealth_amount[i][-1]-invested[i])>0 else "\033[31m")+"{:>7} %\033[37m) ("+("\033[32m" if (wealth_amount[i][-1]-invested[i])>0 else "\033[31m")+"{:>8}\033[37m) [{:>7.3f}] {:7}").format(fullname, wealth, diff_in_percent,diff,current_holding[i],history))
					if inv_type=="liq": print("{:35}: {:.2f}".format(fullname, liquidity[0]))
				diff_in_tot = (total-total_inv)
				diff_in_tot = ("+" if diff_in_tot>0 else "")+"{:.2f}".format(diff_in_tot)
				history_tot = ""
				for i in range(5):
					history_tot = bash_mode_arrows[str(total_5dhistory[-1-i]>total_5dhistory[-2-i])]+history_tot
				history_tot += " "+bash_mode_arrows_bold[str(total_5dhistory[-1]>total_5dhistory[-6])]
				print(("{:35}: {:7.2f} ("+("\033[1;32m" if (total-total_inv)>0 else "\033[1;31m")+"{:>7.2f} %\033[0;37m) ("+("\033[1;32m" if (total-total_inv)>0 else "\033[1;31m")+"{:>8}\033[0;37m) {:9} {:7}").format("Total (w/o Liquidity)", total,100*(total-total_inv)/total_inv,diff_in_tot,"",history_tot))
			
			if mode_history_days>0:
				ncols = len(wealth_amount)
				names = []
				for j in range(len(wealth_amount)-1): names.append(str(config[str(config.sections()[j])]["name"]))
				topbar2 = ("{:10} "+(ncols-1)*"{:>10} ").format("Dates",*names)
				if mode_only_state:
					print("="*(len(topbar)+1))
				else:
					print("="*(len(topbar2)+1))
				print(topbar2)
				print("-"*(len(topbar2)+1))
				for i in range(mode_history_days):
					values = []
					for j in range(ncols-1): values.append(wealth_amount[j][-i-1])
					print(("{:10} "+(ncols-1)*"{:>10.2f} ").format(wealth_dates[0][-i-1],*values))
