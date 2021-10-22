# gsheet2UDMI

## Installation

Create a virtual environment

```
python3 -m pip venv env
```
```
source env/bin/activate
```
```
pip3 install -r requirements.txt
```

## Google Sheet Template format

TODO

## Execution

```
$ ./gsheet2udmi.py -h
           _               _   ____  _   _ ____  __  __ ___
  __ _ ___| |__   ___  ___| |_|___ \| | | |  _ \|  \/  |_ _|
 / _` / __| '_ \ / _ \/ _ \ __| __) | | | | | | | |\/| || |
| (_| \__ \ | | |  __/  __/ |_ / __/| |_| | |_| | |  | || |
 \__, |___/_| |_|\___|\___|\__|_____|\___/|____/|_|  |_|___|
 |___/

usage: gsheet2udmi.py [-h] [-v] [-s GSHEETID] [-w WORKSHEET] [-g GATEWAY] [-j CREDSFILE] [-c CLOUDREGION] [-r REGISTRYID]
                      [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase the verbosity level
  -s GSHEETID, --gsheetid GSHEETID
                        google spreadsheet ID with devices
  -w WORKSHEET, --worksheet WORKSHEET
                        google spreadsheet worksheet
  -g GATEWAY, --gateway GATEWAY
                        gateway device (optional)
  -j CREDSFILE, --credsfile CREDSFILE
                        credential json file
  -c CLOUDREGION, --cloudregion CLOUDREGION
                        GCP region
  -r REGISTRYID, --registryid REGISTRYID
                        GCP Cloud IoT Registry
  -o OUTPUT, --output OUTPUT
                        output folder for the generated UDMI site model
```
