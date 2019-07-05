# Deka
A small python script helping to get a better insight into the temporary evolution of your DekaBank investments.
The script does not directly access your banking account, rather deriving every information from your monthly investments, which are stored in .csv files (~Excel sheets) as plain text.

Primarily developed on MacOS X Mojave (10.14), tested on Linux Mint 18.2 Sonya. Windows support planned.

Dependencies: plotly (used for the interactive plots), wxPython (for the GUI), which are available via pip.

# Setup
1. You will need to install [plotly](https://plot.ly/python/getting-started/) via:
```
pip3 install plotly
```
2. Next, install [wxpython](https://wiki.wxpython.org/How%20to%20install%20wxPython)

3. If you want to launch the script in CLI-mode you have to set the terminals font to one of the [Nerd Fonts](https://nerdfonts.com). To see the available commands type
```
python deka.py --help


4. Under OS X you can launch the script via
```
pythonw deka.py
```

# Screenshots

![Alt text](/screenshots/s1.png?raw=true "")
![Alt text](/screenshots/s2.png?raw=true "")
![Alt text](/screenshots/s3.png?raw=true "")
