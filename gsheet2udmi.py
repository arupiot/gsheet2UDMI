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
import udmi
import datetime

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
class gsheet2UDMI:

    def __init__(self,
                 spreadsheet_id,
                 sheet,
                 credentials_file_path,
                 gateway
                 ):

        self.spreadsheet_id = spreadsheet_id
        self.sheet = sheet
        self.creds = credentials_file_path
        self.gateway = gateway
        self.site_name = ""
        self.devices = []

    def _process_device_row(self, row, outputfolder):
        # if an asset name has been assigned
        if row['asset_name'] != "":
            self.devices.append(row['asset_name'])
            timestamp = datetime.datetime.utcnow()
            x = row['x']
            y = row['y']
            if x == "": x = 0
            if y == "": y = 0
            system = {
                "location": {
                    "site": "%s" % self.site_name,
                    "position": {
                        "x": float(x),
                        "y": float(y),
                    }
                },
                "physical_tag": {
                    "asset": {
                        "guid": "uuid://%s" % row['asset_guid'],
                        "site": "%s" % self.site_name,
                        "name": "%s" % row['asset_name']
                    }
                }
            }

            cloud =  { 
                "is_gateway": False
            }

            gateway = {
                "gateway_id" : self.gateway
            }

            pointset = {
                "points": {
                }
            }

            if row['dbo_pointnames'] != "":
                pointset = {
                    "points": {point:{} for point in row['dbo_pointnames'].split()}
                }

            # metadata = udmi.MetaData(timestamp, system, pointset=pointset, cloud=cloud)
            metadata = udmi.MetaData(timestamp, system, pointset=pointset, gateway = gateway)
            udmi_string = metadata.as_udmi()
            print(row['asset_name'],)
            # create device folder
            device_folder_name = os.path.join(outputfolder, "devices", row['asset_name'])
            # print(device_folder_name)
            if not os.path.exists(device_folder_name):
                os.mkdir(device_folder_name)
            # save metadata.json file into device folder
            metadata_file_name = os.path.join(device_folder_name, "metadata.json")
            # print(metadata_file_name)
            if not os.path.exists(metadata_file_name):
                f = open(metadata_file_name, "w")
                #print(udmi_string)
                f.write(udmi_string)
                f.close()

    def _process_gateway_row(self, row, worksheet, outputfolder):
        # find the gateway that has the same name as the connector and create UDMI metadata file
        if row['connector_name'] == worksheet:
            timestamp = datetime.datetime.utcnow()
            system = {
                "location": {
                    "site": "%s" % self.site_name,
                    "section": "%s" % row['space_name'],
                    "position": {
                        "x": float(row['x']),
                        "y": float(row['y']),
                    }
                },
                "physical_tag": {
                    "asset": {
                        "guid": "uuid://%s" % row['asset_guid'],
                        "site": "%s" % self.site_name,
                        "name": "%s" % row['asset_name']
                    }
                }
            }

            cloud =  {
                "auth_type": "RS256",
                "is_gateway": True
            }

            gateway = {
                "proxy_ids": [device for device in self.devices]
            }

            pointset = {
                "points": {
                }
            }

            if row['dbo_pointnames'] != "":
                pointset = {
                    "points": {point:{} for point in row['dbo_pointnames'].split()}
                }

            metadata = udmi.MetaData(timestamp, system, gateway=gateway, pointset=pointset, cloud=cloud)
            # metadata = udmi.MetaData(timestamp, system, gateway=gateway, pointset=pointset)
            udmi_string = metadata.as_udmi()
            print(row['connector_name'], row['asset_name'])
            #print(udmi_string)
            # create gateway folder
            device_folder_name = os.path.join(outputfolder, "devices", row['asset_name'])
            # print(device_folder_name)
            if not os.path.exists(device_folder_name):
                os.mkdir(device_folder_name)
            # save metadata.json file into device folder
            metadata_file_name = os.path.join(device_folder_name, "metadata.json")
            # print(metadata_file_name)
            if not os.path.exists(metadata_file_name):
                f = open(metadata_file_name, "w")
                #print(udmi_string)
                f.write(udmi_string)
                f.close()


    def convert_to_UDMI_sitemodel(self, outputfolder, cloudregion, registryid):
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds, SCOPES)
        client = gspread.authorize(creds)
        sh = client.open_by_key(self.spreadsheet_id)
        project_wks = sh.worksheet("project")
        gateways_wks = sh.worksheet("gateways")
        devices_wks = sh.worksheet(self.sheet)

        # process project
        p_data = project_wks.get_all_values()
        p_headers = p_data.pop(0)
        p_df = pd.DataFrame(p_data, columns=p_headers)
        self.site_name = p_df.iloc[0]['project_name']
        print("Site name:", self.site_name)

        # create cloud_iot_config.json file
        cic_filename = os.path.join(outputfolder, "cloud_iot_config.json")
        if not os.path.exists(cic_filename):
            f = open(cic_filename, "w")
            config = """{
"cloud_region": "%s",
"site_name": "%s",
"registry_id": "%s"
}""" % (cloudregion, self.site_name, registryid)
            f.write(config)
            f.close()

        # process devices
        d_data = devices_wks.get_all_values()
        d_headers = d_data.pop(0)
        d_df = pd.DataFrame(d_data, columns=d_headers)
        d_df.apply(self._process_device_row, outputfolder = outputfolder, axis=1)

        #print(self.devices)

        # process gateways
        gw_data = gateways_wks.get_all_values()
        gw_headers = gw_data.pop(0)
        gw_df = pd.DataFrame(gw_data, columns=gw_headers)
        gw_df.apply(self._process_gateway_row, worksheet = self.sheet, outputfolder = outputfolder, axis=1)


def main():
    show_title()

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true", default=False, help="increase the verbosity level")
    parser.add_argument("-s", "--gsheetid", default="", help="google spreadsheet ID with devices")
    parser.add_argument("-w", "--worksheet", default="Sheet1", help="google spreadsheet worksheet")
    parser.add_argument("-g", "--gateway", default="", help="gateway device (optional)")
    parser.add_argument("-j", "--credsfile", default=False, help="credential json file")
    parser.add_argument("-c", "--cloudregion", default="europe-west1", help="GCP region")
    parser.add_argument("-r", "--registryid", default="iot-registry", help="GCP Cloud IoT Registry")
    parser.add_argument("-o", "--output", default="udmi_site_model", help="output folder for the generated UDMI site model")

    args = parser.parse_args()

    SPREADSHEET_ID = args.gsheetid
    WORKSHEET = args.worksheet
    GATEWAY = args.gateway
    CREDENTIAL_FILE_PATH = args.credsfile
    OUTFOLDER = args.output
    CLOUDREGION = args.cloudregion
    REGISTRY_ID = args.registryid

    if args.verbose:
        print("Program arguments:")
        print(args)
        print()

    if SPREADSHEET_ID == '':
        print('Convert a Google Sheet building matrix worksheet to a UDMI site model')
        print()
        print('Please provide an Google Sheet ID')
        print('Invoke %s -h for further information\n' % argv[0])
        exit(1)
    else:

        if not WORKSHEET:
           WORKSHEET = 'Sheet1'

        if not OUTFOLDER:
            OUTFOLDER = 'udmi_site_model'

        pwd = os.getcwd()
        OUTFOLDER = os.path.join(pwd,OUTFOLDER)
        print('Output UDMI Site model folder: %s' % OUTFOLDER)

        if not os.path.exists(OUTFOLDER):
            os.mkdir(OUTFOLDER)
        if not os.path.exists(os.path.join(OUTFOLDER,"devices")):
            os.mkdir(os.path.join(OUTFOLDER,"devices"))

        inputfile = gsheet2UDMI(SPREADSHEET_ID, WORKSHEET, CREDENTIAL_FILE_PATH, GATEWAY)
        inputfile.convert_to_UDMI_sitemodel(OUTFOLDER, CLOUDREGION, REGISTRY_ID)

if __name__ == "__main__":
    main()
