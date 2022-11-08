#!/usr/bin/env python3
#
###############################################################################
#   Copyright (C) 2022 Jean-Michel Cohen, F4JDN <f4jdn@outlook.fr>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#
#   Tool to create an activesubscribers.json from log file
#
################################################################################

# Standard modules
import json
import logging
import urllib.request
import platform
import os

# Specific functions to import from standard modules
from time import time
from datetime import timedelta

# Configuration variables and constants
from config import *

# MYSQL stuff (pip install mysql-connector-python)
# from mysql.connector import connect, Error
# import pandas as pd

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CURSORON = '\033[?25h'
    CURSOROFF = '\033[?25l'

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def daydiff(t2):
    return (time()-t2)/1000/3600/24

# https://database.radioid.net/static/users.json
def getRadioIdUserFile():
    fileurl = "https://database.radioid.net/static/users.json"
    logging.info('requesting: %s', fileurl)

    filename = str(fileurl.rsplit('/', 1)[-1])
    filepath = PATH + "assets/" + filename

    print("checking if " + filepath + " exists")
    if os.path.exists(filepath):
        print("checking if " + filename + " needs new download from remote")
        if daydiff(creation_date(filepath)) < 7:
            print("yes, and  " + filename + " recent enough, no download needed")
            return filename

    print(filename + " is missing or older than 7 days, download")
    with urllib.request.urlopen(fileurl) as url:
        with open(filepath, 'w') as users_json:
            users_json.write(url.read().decode("utf-8"))
            print(filename + " downloaded and saved")
            return filename

def fetchRemoteUsersFiles(fileurl):
    if fileurl != "":
        logging.info('requesting: %s', fileurl)

        filename = str(fileurl.rsplit('/', 1)[-1])
        filepath = PATH + "assets/" + filename

        if filename == "active_subscriber_ids.json":
            print("get worldwide users file from radioid")
            radioidusers = getRadioIdUserFile()

            print("checking for radioid file")
            if radioidusers != "":
                print("ok, load radioidusers")
                with open(PATH + "assets/" + radioidusers, 'r') as radioidfile:
                    radioidsubscribers = json.load(radioidfile)
                    print("checking radioid file validity")
                    if radioidsubscribers.get("users"):
                        radioidsubscribers = radioidsubscribers["users"]

                        print("ok, load localid subscribers")
                        with open(PATH + "local_subscriber_ids.json", 'r') as localidfile:
                            localidsubscribers = json.load(localidfile)
                            print("checking for valid localsubscribers file")
                            if localidsubscribers.get("results"):
                                localidsubscribers = localidsubscribers["results"]

                                print("ok, load local server lastheardusers")
                                with open(LOG_PATH + "lastheard.json", 'r+') as lastheardfile:
                                    traffic = json.load(lastheardfile)

                                    print("ok, checking for valid lastheardusers")
                                    if traffic.get("TRAFFIC"):
                                        print("ok, starting parse")
                                        lastheardusers = traffic["TRAFFIC"]

                                        del traffic
                                        activeUsers = {}
                                        
                                        # create lastheard users dict
                                        for record in lastheardusers:
                                            # read END packets only
                                            if record["PACKET"] != "START":
                                                activeUsers.update({ record['DMRID']: record })

                                        # get dict count
                                        count = len(activeUsers)

                                        # if count not 0, start to work
                                        if count > 0:
                                            jsonStr = {
                                                    "count": count,
                                                    "results": []
                                                }

                                            # prepare progression bar
                                            print("\r\nParsing the " + str(count) + " active users found" + f"{bcolors.CURSOROFF}")
                                            maxprogbarlength = 40
                                            ratio = maxprogbarlength / count
                                            t1 = time()*1000-1
                                            treated = 0

                                            # loop throughout the dict (enumerate to get the loop index)
                                            for index, key in enumerate(activeUsers):
                                                elapsed = (time()*1000 - t1)
                                                speed = int(elapsed/(index+1))
                                                eta = timedelta(seconds=int((count-index)/speed))

                                                green = int((index+1)*ratio)
                                                white = int(maxprogbarlength-green)
                                                #     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 4.2 MB/s eta 0:00:00
                                                print(" "*5+f"{bcolors.GREEN}"+"━"*green + f"{bcolors.ENDC}" + "━"*white + str(index+1).rjust(6, ' ') + "/" + str(count) \
                                                    + " "+f"{bcolors.RED}" + str(speed) + "rec/s"+ f"{bcolors.ENDC}" \
                                                    + " "+f"{bcolors.ENDC}" + "eta " + str(eta), end="\r")
                                                record = activeUsers[key]
                                                found = False

                                                #
                                                # first look for a match in radioidsubscribers
                                                #
                                                for om in radioidsubscribers:
                                                    if om["id"] == int(record["DMRID"]):
                                                        om["surname"] = om["surname"].strip()
                                                        if not om.get("remarks"):
                                                            om["remarks"] = ""

                                                        jsonStr["results"].append(om)
                                                        found = True
                                                        break

                                                #
                                                # then, if not found look for a match in localidsubscribers
                                                #
                                                if not found:
                                                    if localidsubscribers:
                                                        for om in localidsubscribers:
                                                            if om["id"] == int(record["DMRID"]):
                                                                om["surname"] = om["surname"].strip()
                                                                if not om.get("remarks"):
                                                                    om["remarks"] = ""

                                                                jsonStr["results"].append({
                                                                    "fname":  om["fname"],
                                                                    "name": om["surname"],
                                                                    "country": om["country"],
                                                                    "callsign": om["callsign"].strip(), 
                                                                    "city": om["city"], 
                                                                    "surname": om["surname"],
                                                                    "radio_id": om["id"], 
                                                                    "id": om["id"], 
                                                                    "remarks": "",
                                                                    "state": om["state"]
                                                                })

                                                                found = True
                                                                break
                                                    
                                                    #
                                                    # then, if still not found create a record from data we have
                                                    #
                                                    if not found:
                                                        jsonStr["results"].append({
                                                            "fname": "",
                                                            "name": "",
                                                            "country": "",
                                                            "callsign": record["CALLSIGN"].strip(), 
                                                            "city": "", 
                                                            "surname": record["NAME"].strip(),
                                                            "radio_id": int(record["DMRID"]), 
                                                            "id": int(record["DMRID"]), 
                                                            "remarks": "",
                                                            "state": ""
                                                        })

                                            # save the file
                                            with open(PATH + "assets/" + filename, 'w+') as file:
                                                file.seek(0)
                                                json.dump(jsonStr, file, indent=4)
                                                file.truncate()

                                            print("done! \r\n")
                                        else:
                                            print("zero records found")
                                    else:
                                        print("bad lastheard file")
                            else:
                                print("bad local subscribers file")
                    else:
                        print("bad radioid file")
    print(f"{bcolors.CURSORON}")

if __name__ == '__main__':
    fetchRemoteUsersFiles("http://francophonie.link/active_subscriber_ids.json")
