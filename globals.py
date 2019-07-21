import os
import sys
import csv
import time
import configparser
import requests

from datetime import date
import datetime

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

def print_if_allowed(*string):
	global printing_allowed
	if printing_allowed: print(*string)