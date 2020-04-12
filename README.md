# Deka
A small python script helping to get a better insight into the temporal evolution of your DekaBank investments.
The script does not directly access your banking account, rather deriving every information from your monthly investments, which are stored in (encrypted) .csv files (~Excel sheets).

Primarily developed on MacOS X Catalina (10.15), tested on Linux Mint 18.2 Sonya. Windows support planned.

Dependencies: plotly (used for the interactive plots), wxPython (for the GUI), the cryptography library (for the encryptions) all of which are available via pip.

Under Ubuntu you might need to build wxpython yourself, for which its dependecies have to be installed first:
```
sudo apt-get install dpkg-dev build-essential python3.7-dev libpython3.7-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev
```
Then, one can execute
```
pip3 install wxpython
```



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

# Encryption
By default, the .csv-sheets are not encrypted in order facilitate the setup procedure. Once ready, these files can be encrypted via
```
deka encrypt
```
and eventually decrypted through
```
deka decrypt
```
if further edits and changes are needed.

# Password
During the first launch, you will need to setup your login password, which can be changed anytime by typing
```
deka passwd
```

# Terminal outputs
Launching ```pythonw deka.py -s``` one gets a brief up-to-date summary about the investments in the command line without opening the app. The output looks something like the following:

![Alt text](/screenshots/deka_s.png?raw=true "")

Typing ```pythonw deka.py --hist n``` prints the history of every investment up to the last n days. One can combine it with the prevoius one as ```pythonw deka.py -s --hist 7```.

# Screenshots

![Alt text](/screenshots/s1.png?raw=true "")
![Alt text](/screenshots/s2.png?raw=true "")
![Alt text](/screenshots/s3.png?raw=true "")
