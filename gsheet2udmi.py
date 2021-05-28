#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyfiglet import Figlet
import argparse
from sys import argv, exit
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
from string import Template
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

__author__ = "Francesco Anselmo"
__copyright__ = "Copyright 2021, Francesco Anselmo"
__credits__ = ["Francesco Anselmo"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Francesco Anselmo"
__email__ = "francesco.anselmo@gmail.com"
__status__ = "Dev"

SCOPES = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

def show_title():
    """Show the program title
    """
    f1 = Figlet(font='standard')
    print(f1.renderText('gsheet2UDMI'))

def get_gsheet(spreadsheet_id, sheet, credentials_file_path):
    return gsheet2UDMI(spreadsheet_id, sheet, credentials_file_path)

class gsheet2UDMI:

    def __init__(self,
                 spreadsheet_id,
                 sheet,
                 credentials_file_path,
                 ):

        self.spreadsheet_id = spreadsheet_id
        self.sheet = sheet
        self.creds = credentials_file_path

    def convert_to_UDMI_sitemodel(self, outputfolder):
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds, SCOPES)
        client = gspread.authorize(creds)
        sh = client.open_by_key(self.spreadsheet_id)
        wks = sh.worksheet(self.sheet)

        data = wks.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        print(df)


def main():
    show_title()

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true", default=False, help="increase the verbosity level")
    parser.add_argument("-s", "--gsheetid", default='', help="google spreadsheet ID")
    parser.add_argument("-w", "--worksheet", default="Sheet1", help="google spreadsheet worksheet")
    parser.add_argument("-j", "--credsfile", default=False, help="credential json file")
    parser.add_argument("-o", "--output", default="output", help="output folder for the generated UDMI site model")

    args = parser.parse_args()

    SPREADSHEET_ID = args.gsheetid
    WORKSHEET = args.worksheet
    CREDENTIAL_FILE_PATH = args.credsfile
    OUTFOLDER = args.output

    if args.verbose:
        print("Program arguments:")
        print(args)
        print()

    if SPREADSHEET_ID == '':
        print('Please provide an Google Sheet ID')
        print('Invoke %s -h for further information.\n' % argv[0])
        exit(1)
    else:

        if not WORKSHEET:
           WORKSHEET = 'Sheet1'

        if not OUTFOLDER:
            OUTFOLDER = 'udmi_site_model'

        pwd = os.getcwd()
        print('Output UDMI Site model folder: %s' % (pwd+'/'+OUTFOLDER))

        if not os.path.exists(OUTFOLDER):
            os.mkdir(OUTFOLDER)

        inputfile = get_gsheet(SPREADSHEET_ID, WORKSHEET, CREDENTIAL_FILE_PATH)
        inputfile.convert_to_UDMI_sitemodel(OUTFOLDER)

if __name__ == "__main__":
    main()
