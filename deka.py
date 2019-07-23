import sys
import requests

import globals

bash_terminal_font_patched = True #if patched fonts are used, set True; otherwise only standard Unicode characters will be used

if bash_terminal_font_patched:
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
					if args[args.index("--hist")+1][0]!="-": print("Warning: could not convert",args[args.index("--hist")+1],"to int; default: 10")
					globals.mode_history_days = 10
				if globals.mode_history_days <= 0:
					print("Warning: ",globals.mode_history_days,"is smaller then 0; returning to default: 10")
					globals.mode_history_days = 10
			else:
				globals.mode_history_days = 10
		globals.print_if_allowed("Welcome!")
		globals.readIn_and_update_Data()
		try:
			if not globals.mode_CLI:
				import gui
				gui.gui_init("Online Mode")
		except requests.exceptions.ConnectionError:
			globals.print_if_allowed("Connection Error, starting in offline mode...")
			if not globals.mode_CLI: gui_init("Offline Mode")
		if not globals.mode_CLI:
			globals.print_if_allowed("Starting Application...")
			gui.gui_main_loop()
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
						diff_in_percent = ((globals.wealth_amount[i][-1]-globals.invested[i])/globals.invested[i])*100
						diff_in_percent = ("+" if diff_in_percent>0 else "")+"{:.2f}".format(diff_in_percent)
						diff = (globals.wealth_amount[i][-1]-globals.invested[i])
						diff = ("+" if diff>0 else "")+"{:.2f}".format(diff)
						history = ""
						for j in range(6):
							total_5dhistory[5-j] += globals.wealth_amount[i][-1-j]
							if j!=5:
								history = bash_mode_arrows[str(globals.wealth_amount[i][-1-j]>globals.wealth_amount[i][-2-j])]+history
								if globals.wealth_amount[i][-1-j]==globals.wealth_amount[i][-2-j]: history = "\033[33m"+bash_mode_arrows_stagnation+"\033[37m"+history[len(bash_mode_arrows[str(globals.wealth_amount[i][-1-j]>globals.wealth_amount[i][-2-j])]):]
						history += " "+bash_mode_arrows_bold[str(globals.wealth_amount[i][-1]>globals.wealth_amount[i][-6])]
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
				ncols = len(globals.wealth_amount)*2
				headline = []
				prices = []
				for j in range(len(globals.wealth_amount)-1):
					name = str(globals.config[str(globals.config.sections()[j])]["name"])
					headline.append(name)
					headline.append("Price")
					x,p_buy,p_sell = globals.parseDekaData(j,name) #reading in data...
					prices.append(p_sell[-globals.mode_history_days:])
				topbar2 = ("{:10} "+int(ncols*0.5-1)*"{:^8} {:^8}").format("Dates",*headline)
				if globals.mode_only_state:
					print("="*(len(topbar)+1))
				else:
					print("="*(len(topbar2)+1))
				print(topbar2)
				print("-"*(len(topbar2)+1))
				for i in range(globals.mode_history_days):
					values = []
					for j in range(ncols-1):
						if j%2 == 1:
							values.append(prices[int((j-1)*0.5)][-i-1])
						else:
							values.append(globals.wealth_amount[int(j/2)][-i-1])
					print(("{:10} "+int(ncols*0.5-1)*"{:>8.2f} {:>8.2f}").format(globals.wealth_dates[0][-i-1],*values))
