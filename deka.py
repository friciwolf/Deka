import sys

import globals

from encryption import decryptCSVs
from encryption import encryptCSVs
from encryption import changePassword

if globals.bash_terminal_font_patched:
	bash_mode_arrows = {"True":"\033[32m\uf55b\033[37m","False":"\033[31m\uf542\033[37m"} #up, down
	bash_mode_arrows_bold = {"True":"\033[32m\uf062\033[37m","False":"\033[31m\uf063\033[37m"} #up, down
	bash_mode_arrows_stagnation = "\uf553"
else:
	bash_mode_arrows = {"True":"\033[32m\u2197\033[37m","False":"\033[31m\u2198\033[37m"} #up, down
	bash_mode_arrows_bold = {"True":"\033[32m\u21e7\033[37m","False":"\033[31m\u21e9\033[37m"} #up, down
	bash_mode_arrows_stagnation = "\u2192"

if __name__ == '__main__':
	args = sys.argv
	if ("--help" in args) or ("-h") in args:
		print("DekaPlotter")
		print("  Arguments:")
		print("{:4} {:25} - {}".format("","--msg, --msgs or -m","Shows startup progress"))
		print("{:4} {:25} - {}".format("","--status, --state or -s","Shows data only in terminal"))
		print("{:4} {:25} - {}".format("","--hist n", "Shows investement history of the past n (def: 10) days"))
		print("{:4} {:25} - {}".format("","--cached, -c", "Uses cached data"))
		print("{:4} {:25} - {}".format("","--no-graphs, -g", "Does not create graphs increasing startup time"))
		print("{:4} {:25} - {}".format("","encrypt", "Encrypts the datafiles"))
		print("{:4} {:25} - {}".format("","decrypt", "Decrypts the datafiles"))
		print("{:4} {:25} - {}".format("","passwd", "Changes the password"))
		exit()
	elif "decrypt" in args:
		if globals.files_encrypted==True:
			decryptCSVs(globals.encryption_salt,globals.config)
			globals.settings["settings"]["encrypted"]="0"
		else:
			print("Datasets already decrypted.")
	elif "encrypt" in args:
		if globals.files_encrypted==False:
			encryptCSVs(globals.encryption_salt,globals.config)
			globals.settings["settings"]["encrypted"]="1"
		else:
			print("Datasets already encrypted.")
	elif "passwd" in args:
		changePassword(globals.config,globals.settings,globals.encryption_salt,globals.files_encrypted)
	else:
		if ("--msg" in args) or ("--msgs" in args) or ("-m" in args): globals.printing_allowed = True
		if ("--status" in args) or ("--state" in args) or ("-s" in args):
			globals.mode_only_state = True
			globals.mode_CLI = True
		if "--hist" in args:
			globals.mode_CLI = True
			if args.index("--hist")+1<len(args):
				try:
					globals.mode_history_days = int(args[args.index("--hist")+1])
				except ValueError:
					if args[args.index("--hist")+1][0]!="-": print("\033[30;43mWarning:\033[0m  could not convert","'"+args[args.index("--hist")+1]+"'","to int; using default: 10")
					globals.mode_history_days = 10
				if globals.mode_history_days <= 0:
					print("\033[30;43mWarning:\033[0m ",globals.mode_history_days,"is smaller then 0; returning to default: 10")
					globals.mode_history_days = 10
			else:
				globals.mode_history_days = 10
		globals.print_if_allowed("Welcome!")
		if ("--cached" in args) or ("-c" in args):
			globals.launchWithUpdate = False
			print("Using cached data...")
		if ("--no-graphs" in args) or ("-g" in args):
			globals.createGraphsAtStartup = False
		if globals.files_encrypted==False:
			print("\033[97;41mWarning:\033[0m Dataset files are not encrypted")
		globals.readIn_and_update_Data(globals.launchWithUpdate)
		if not globals.mode_CLI:
			globals.readInScopeAnalysisData(globals.launchWithUpdate)
			import gui
			if globals.createGraphsAtStartup: gui.gui_make_plots()
			globals.print_if_allowed("Starting Application...")
			if globals.launchWithUpdate==True:
				gui.gui_main_loop("Online Mode" if len(globals.error_connection_deka_server)==0 else "Offline Mode")
			else:
				gui.gui_main_loop("Data taken from stored cache")
		else:
			if globals.mode_only_state:
				topbar = "{:35}: {:7} ({:7}) ({:>7}) [{:7}] {:8}".format("Product name", "Value", "Gain/Loss","Real G/L","C.Hold.","Hist(5d)")
				print("="*(len(topbar)+1))
				print(topbar)
				print("-"*(len(topbar)+1))
				total = 0.0
				total_inv = 0.0
				total_5dhistory = 6*[0] #6-days ago;5 days ago;...;today
				for i in range(len(globals.wealth_amount)):
					inv_type = str(globals.config[str(globals.config.sections()[i])]["type"])
					fullname = str(globals.config[str(globals.config.sections()[i])]["fullname"])
					wealth = globals.wealth_amount[i][-1]
					if inv_type=="deka":
						total += wealth
						total_inv += globals.invested[i]
						try:
							diff_in_percent = ((globals.wealth_amount[i][-1]-globals.invested[i])/globals.invested[i])*100							
							diff_in_percent = ("+" if diff_in_percent>0 else "")+"{:.2f}".format(diff_in_percent)
						except ZeroDivisionError:
							diff_in_percent = "---"
						diff = (globals.wealth_amount[i][-1]-globals.invested[i])
						diff = ("+" if diff>0 else "")+"{:.2f}".format(diff)
						history = ""
						try:
							for j in range(6):
								total_5dhistory[5-j] += globals.wealth_amount[i][-1-j]
								if j!=5:
									history = bash_mode_arrows[str(globals.wealth_amount[i][-1-j]>globals.wealth_amount[i][-2-j])]+history
									if globals.wealth_amount[i][-1-j]==globals.wealth_amount[i][-2-j]: history = "\033[33m"+bash_mode_arrows_stagnation+"\033[37m"+history[len(bash_mode_arrows[str(globals.wealth_amount[i][-1-j]>globals.wealth_amount[i][-2-j])]):]
							history += " "+bash_mode_arrows_bold[str(globals.wealth_amount[i][-1]>globals.wealth_amount[i][-6])]
						except IndexError:
							pass
						print(("{:35}: {:7.2f} ("+("\033[32m" if (globals.wealth_amount[i][-1]-globals.invested[i])>0 else "\033[31m")+"{:>7} %\033[37m) ("+("\033[32m" if (globals.wealth_amount[i][-1]-globals.invested[i])>0 else "\033[31m")+"{:>8}\033[37m) [{:>7.3f}] {:7}").format(fullname, wealth, diff_in_percent,diff,globals.current_holding[i],history))
					if inv_type=="liq": print("{:35}: {:.2f}".format(fullname, globals.liquidity[0]))
				diff_in_tot = (total-total_inv)
				diff_in_tot = ("+" if diff_in_tot>0 else "")+"{:.2f}".format(diff_in_tot)
				history_tot = ""
				for i in range(5):
					history_tot = bash_mode_arrows[str(total_5dhistory[-1-i]>total_5dhistory[-2-i])]+history_tot
				history_tot += " "+bash_mode_arrows_bold[str(total_5dhistory[-1]>total_5dhistory[-6])]
				print(("{:35}: {:7.2f} ("+("\033[1;32m" if (total-total_inv)>0 else "\033[1;31m")+"{:>7.2f} %\033[0;37m) ("+("\033[1;32m" if (total-total_inv)>0 else "\033[1;31m")+"{:>8}\033[0;37m) {:9} {:7}").format("Total (w/o Liquidity)", total,100*(total-total_inv)/total_inv,diff_in_tot,"",history_tot))

			if globals.mode_history_days>0:
				nb_products = len(globals.wealth_amount)
				for j in range(nb_products): #removing liquidity and co.
					if str(globals.config[str(globals.config.sections()[j])]["type"])!="deka": nb_products-=1
				headline = []
				prices = []
				for j in range(nb_products):
					name = str(globals.config[str(globals.config.sections()[j])]["name"])
					headline.append(name)
					headline.append("Price")
					x,p_buy,p_sell = globals.parseDekaData(j,name) #reading in data...
					prices.append(p_sell[-globals.mode_history_days:])
				topbar2 = ("{:10}"+nb_products*" | {:^8}  {:<6}").format("Dates",*headline)
				if globals.mode_only_state:
					print("="*(len(topbar)+1))
				else:
					print("="*(len(topbar2)+1))
				print(topbar2)
				print("-"*(len(topbar2)+1))
				for i in range(globals.mode_history_days):
					values = []
					for j in range(nb_products):
						try:
							values.append(globals.wealth_amount[j][-i-1])
							values.append(prices[j][-i-1])
						except IndexError:
							values.append(0)
							values.append(0)
					print(("{:10}"+nb_products*" | {:>8.2f}  {:>6.2f}").format(globals.wealth_dates[0][-i-1],*values))
	globals.closeAndCleanup()