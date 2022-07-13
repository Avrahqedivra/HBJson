#!/usr/bin/env python3
#

###############################################################################
#   Copyright (C) 2022 Jean-Michel Cohen, F4JDN <avrahqedivra@gmail.com>
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
###############################################################################

# Standard modules
import json
import logging
import sys
import csv
import re

from itertools import islice
from datetime import datetime

# https://realpython.com/python-mysql/#installing-mysql-connectorpython
from mysql.connector import connect, Error

# Configuration variables and constants
from config import *

names_dict = { "Andre":"André", "Francois":"François", "Herve":"Hervé", "Jerome":"Jérôme", "Jerôme":"Jérôme",
            "Stephane":"Stéphane", "Gerard":"Gérard", "Jean-Noel":"Jean-Noël", "Remi":"Rémi", "Clement":"Clément",
            "Frederic":"Frédéric", "Jeremy":"Jérémy", "Jean-Francois":"Jean-François", "Gregory":"Grégory", "Anne-Cecile":"Anne-Cécile",
            "Mickael":"Mickaël", "Theophile":"Théophile", "Sebastien":"Sébastien", "Raphael":"Raphaël", "Cedric":"Cédric", 
            "Rene":"René", "Nathanael":"Nathanaël", "Joel":"Joël", "Jeremie":"Jérémie"
        }

overwrite = False

def checkNULL(field):
    if not field or field == None:
        return ""
        
    return field

# https://stackoverflow.com/questions/1549641/how-can-i-capitalize-the-first-letter-of-each-word-in-a-string
def enhanceNames(name):
    if name in names_dict:
        return re.sub(r"/(?:^|\s|['`‘’.-])[^\x00-\x60^\x7B-\xDF](?!(\s|$))/g", lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), names_dict[name])

    return name

def localSubscribersToJson():
    global overwrite

    try:
        with connect(host=SQL_HOST, user=SQL_USER,password=SQL_PASS,database=SQL_DATABASE) as connection:
            with connection.cursor(buffered=True) as cursor:
                cursor.execute('select * from local_subscribers;')
                subscribers = cursor.fetchall()

                SUBSCRIBERSJ = []

                for row in subscribers:
                    SUBSCRIBERSJ.append({
                        'fname':        row[0],
                        'name':         row[1], 
                        'surname':      row[2], 
                        'city':         row[3],
                        'state':        row[4],
                        'country':      row[5],
                        'callsign':     row[6],
                        "radio_id":     "",
                        'id':           row[7],
                        'remarks':      row[8]
                    })

                print("overwrite : " + str(overwrite))

                if overwrite == False:
                    # dd/mm/YY H:M:S
                    now = datetime.now()
                    dt = now.strftime("_%m%d_%H%M%S")
                else:
                    dt = ""

                with open("local_subscriber"+dt+"_ids.json", 'w+') as file:
                    file.seek(0)
                    json.dump({ 'count': len(subscribers), "results" : SUBSCRIBERSJ }, file, indent=4)
                    file.truncate()
                    print(file.name + " written with " + str(len(subscribers)) + " records from local_subscribers table")

    except Error as e:
        print("Error {} ", e)

def localSubscribersToSql():
    try:
        with connect(host=SQL_HOST, user=SQL_USER,password=SQL_PASS,database=SQL_DATABASE) as connection:
            with open("local_subscriber_ids.json", 'r') as file:
                subscribers = json.load(file)

                with connection.cursor(buffered=True) as cursor:

                    # get tables list
                    tableNotFound = True
                    cursor.execute("SHOW TABLES")
                    
                    # check if our table is already there
                    for (table,) in cursor:
                        if (table == "local_subscribers"):
                            tableNotFound = False
                            break

                    # create table if does not exist
                    if tableNotFound == True:
                        print("table not found, creating new empty table")
                        cursor.execute("CREATE TABLE local_subscribers ( \
                                            fname VARCHAR(80), \
                                            name VARCHAR(80), \
                                            surname VARCHAR(80), \
                                            city VARCHAR(96), \
                                            state VARCHAR(80), \
                                            country VARCHAR(32), \
                                            callsign VARCHAR(16), \
                                            id VARCHAR(16), \
                                            remarks VARCHAR(80) \
                                          )")
                    else:
                        # delete all rows from table
                        print("table found, deleting previous content")
                        cursor.execute('DELETE FROM local_subscribers;',)

                    # start xith an empty array
                    rows = []

                    # fill it up from json file data
                    for user in subscribers["results"]:

                        callsign = user["callsign"]
                        fname = user["fname"]
                        name = user["name"]
                        surname = user["surname"]
                        id = user["id"]
                        country = user["country"]
                        city = user["city"]
                        dept = user["state"]
                        remarks = user["remarks"]

                        #if remarks == "SHIELD":
                        # if callsign.startswith("FS") and country == "France" and len(city) > 0:
                        #     cursor.execute("SELECT * FROM mediapost WHERE city LIKE('"+city+"')")
                        #     addresses = cursor.fetchall()

                        #     if len(addresses) == 0:
                        #         if "Saint " or " prs " or " ls " in city:
                        #             city = city.replace(" ls ", " les ").replace(" prs ", " pres ").replace("Saint ", "St ")
                        #             cursor.execute("SELECT * FROM mediapost WHERE city LIKE('"+city+"')")
                        #             addresses = cursor.fetchall()

                        #     for address in addresses:
                        #         dept = address[0].strip('"')
                        #         break

                        rows.append((enhanceNames(fname),name,surname,city,dept,country,callsign,id,remarks))

                    
                    # add all the new rows at once
                    cursor.executemany("INSERT INTO local_subscribers (fname,name,surname,city,state,country,callsign,id,remarks) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
                    connection.commit()
                    print("table loaded with " + str(len(rows)) + " records from " + file.name)
                    connection.close()

    except Error as e:
        print("Error {} ", e)

def usage():
    print("[-o] tosql or tojson expected")
    return

def main():
    global overwrite
    
    if len(sys.argv[1:]) == 0:
        print("[-o] tosql or tojson expected")
        return

    fct = usage
    overwrite = False

    for arg in sys.argv[1:]:
        if arg == "tosql":
            fct = localSubscribersToSql
        elif arg == "tojson":
            fct = localSubscribersToJson
        elif arg == "-o":
            overwrite = True

    # run found function
    fct()

if __name__ == '__main__':  
    logging.info(__name__)
    main()



