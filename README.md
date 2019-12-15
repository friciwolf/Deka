# Deka
A small python script helping to get a better insight into the temporal evolution of your DekaBank investments.
The script does not directly access your banking account, rather deriving every information from your monthly investments, which are stored in .csv files (~Excel sheets) as plain text, which can be assigned to an other user account and then be accessed via sudo. Password protection+encryption of the datafiles are planned as features.

Primarily developed on MacOS X Catalina (10.15), tested on Linux Mint 18.2 Sonya. Windows support planned.

Dependencies: plotly (used for the interactive plots), wxPython (for the GUI), both of which are available via pip.

# Setup
1. You will need to install [plotly](https://plot.ly/python/getting-started/) via:
```
pip3 install plotly
```
2. Next, install [wxpython](https://wiki.wxpython.org/How%20to%20install%20wxPython)

3. If you want to launch the script in CLI-mode you have to set the terminal's font to one of the [Nerd Fonts](https://nerdfonts.com). To see the available commands type
```
python deka.py --help
```
You might also want to add the following lines to your .bashrc or .zshrc to lauch the script directly via ```deka```
```
function deka {
	cd /path/to/deka/script
	pythonw deka.py $@
	cd -
	echo -e "\033[2A"
}
```

4. Under OS X you can launch the script via
```
pythonw deka.py
```

# Terminal outputs
Launching ```pythonw deka.py -s``` one gets a brief up-to-date summary about the investments in the command line without opening the app. The output looks something like the following:

![Alt text](/screenshots/deka_s.png?raw=true "")

Typing ```pythonw deka.py --hist n``` prints the history of every investment up to the last n days. One can combine it with the prevoius one as ```pythonw deka.py -s --hist 7```.

# Screenshots

![Alt text](/screenshots/s1.png?raw=true "")
![Alt text](/screenshots/s2.png?raw=true "")
![Alt text](/screenshots/s3.png?raw=true "")
