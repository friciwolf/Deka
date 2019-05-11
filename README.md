# Deka
A small python script helping to get a better insight into the temporary evolution of your DekaBank investments.
The script does not directly access to your banking account, rather deriving every information from your monthly investments, which is stored in .csv files (~Excel sheets) as plain text.

Primarily developed on MacOS X Mojave (10.14), tested on Linux Mint 18.2 Sonya

Dependencies: plotly (used for the interactive plots), wxPython (for the GUI), which are available via pip.

# Setup
1. You will need to install [plotly](https://plot.ly/python/getting-started/) and csvparser via:
```
pip3 install plotly
```
2. Next, install [wxpython](https://wiki.wxpython.org/How%20to%20install%20wxPython)

3. Under OS X you can launch the script via
```
pythonw deka.py
```

# Screenshots

![Alt text](/screenshots/s1.png?raw=true "")
![Alt text](/screenshots/s2.png?raw=true "")
![Alt text](/screenshots/s3.png?raw=true "")
