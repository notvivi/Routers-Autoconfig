# Linux Debian VPS Autoconfiguration
This python script is about autoconfiguring linux debian virtual private servers via ssh


## Requirements
- python 3.10.0 and more
- pyinstaller and paramiko

## How to download pyinstaller
1. Open terminal
2. Copy `pip install pyinstaller` and paste it into terminal, press enter
3. Copy `pip install paramiko` and paste it into terminal, press enter

## How to set up configuration file
- The password `must be the same` for all linux vps
- Your files do not have to be located in this project
- In `src -> config.json` replace configuration with your own

## How to START
1. After setting up everything, open terminal
2. Copy `pyinstaller --onefile --add-data "src/config.json;src" --add-data "lib;lib" --add-data "res;res" --add-data "log;log" src/main.py"` and paste it into terminal, press enter
3. In file explorer, find dist folder and run `main.exe`
4. Enjoy

If you need help with anything, contact me at email vtomanova33@gmail.com.

