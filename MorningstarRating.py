#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 21:39:53 2020

@author: Mate
"""
"""
use URL https://tools.morningstar.de/de/interactivechart/html/default.aspx?embedded=true&SecurityTokenList=F00000J8T2
with id: F00000J8T2

instead of fetching the dataset.
get the rating from:
https://www.morningstar.de/de/funds/snapshot/snapshot.aspx?id=F00000J8T2

"""


import requests
import json
from datetime import datetime

def cutString(string,key_cut):
	for i in range(len(string)):
		if string[i:i+len(key_cut)]==key_cut:
			return string[:i]
	return ""

def findSection(source,key_start,key_end):
	data = ""
	for i in range(len(source)):
		substring = source[i:i+len(key_start)]
		if substring == key_start:
			for j in range(i,len(source)):
				substring2 = source[j:j+len(key_end)]
				if substring2 == key_end:
					data = source[i:j]
					data = data[len(key_start):]
					break
			break
	return data

class ScopeData:
	def loadFromFile(self,path,isin):
			try:
				with open(path, 'r') as file:
					self.url = "https://funds.scopeanalysis.com/portal/en/common/public/fund/"+isin+"/en/home"
					self.html = file.read()
					key_begin = "jQuery(\"#perfAbsMonths\").kendoChart("
					key_end = ");"
					data = findSection(self.html,key_begin,key_end)
					d = json.loads(data)
					self.dates = d["categoryAxis"][0]["categories"] #Structure: mm.yy
					#Conversion to datetime
					for i in range(len(self.dates)):
						date = self.dates[i]
						self.dates[i] = datetime(year=2000+int(date[-2:]),month=int(date[:2]),day=1)
					self.peerPerformance = [] #Structure: 0th element: name; 1st: performance
					for i in range(3):
						a = []
						a.append(cutString(d["series"][i]["tooltip"]["template"],"<br />"))
						a.append(d["series"][i]["data"])
						self.peerPerformance.append(a)
					self.name = self.peerPerformance[0][0]
					self.score,self.rating = self.getScoreAndRating(self.html)
			except FileNotFoundError:
				pass
	
	def getScoreAndRating(self,html):
		score = -99
		score_raws = findSection(html, "<td class=\"center weight\">100 %</td>", "</tr>")
		iters = 0
		ratings = ["A","B","C","D","E","N/A"]
		rating = ratings[-1]
		for i in range(len(score_raws)):
			key_start = "<td class=\"center ratingletter\">"
			key_end = "</td>"
			substring = score_raws[i:i+len(key_start)]
			if substring == key_start:
				for j in range(i,len(score_raws)):
					substring2 = score_raws[j:j+len(key_end)]
					if substring2 == key_end:
						r = score_raws[i:j]
						r = r[len(key_start):]
						if r!= "":
							score = int(r)
							rating = ratings[iters]
							break
						else:
							i=j
							iters+=1
							break
		return score,rating
	
	def __init__(self,isin):
		if isin!="":
			self.url = "https://funds.scopeanalysis.com/portal/en/common/public/fund/"+isin+"/en/home"
			self.html = requests.get(self.url).text
			key_begin = "jQuery(\"#perfAbsMonths\").kendoChart("
			key_end = ");"
			data = findSection(self.html,key_begin,key_end)
			d = json.loads(data)
			self.isin = isin
			self.dates = d["categoryAxis"][0]["categories"]
			#Conversion to datetime
			for i in range(len(self.dates)):
				date = self.dates[i]
				self.dates[i] = datetime(year=2000+int(date[-2:]),month=int(date[:2]),day=1)
			self.peerPerformance = [] #Structure: 0th element: name; 1st: performance
			for i in range(3):
				a = []
				a.append(cutString(d["series"][i]["tooltip"]["template"],"<br />"))
				a.append(d["series"][i]["data"])
				self.peerPerformance.append(a)
			self.name = self.peerPerformance[0][0]
			self.score,self.rating = self.getScoreAndRating(self.html)
		else: #constructor if no isin given
			self.url = ""
			self.html = ""
			self.isin = isin
			self.dates = []
			self.peerPerformance = []
			self.name = ""
			self.score = -99
			self.rating = "N/A"
