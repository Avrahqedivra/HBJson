#!/usr/bin/env python3
#
###############################################################################
#   Copyright (C) 2016-2019  Cortney T. Buffington, N0MJS <n0mjs@me.com>
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
#
#   Python 3 port by Steve Miller, KC1AWV <smiller@kc1awv.net>
#
###############################################################################
###############################################################################
#
#   Version by Waldek SP2ONG
#
###############################################################################
###############################################################################
#
#   JSON service by Avrahqedivra F4JDN, F-16987
#   MYSQL added by  Avrahqedivra F4JDN, F-16987
#
###############################################################################

# Standard modules
import json
import csv
import logging
import time as ptime
import datetime
import base64
import urllib
import platform
import os
import binascii

from urllib import parse

from itertools import islice
from ssl import SSL_ERROR_WANT_X509_LOOKUP
from subprocess import check_call, CalledProcessError
from wsgiref.util import request_uri

# Twisted modules
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import NetstringReceiver, FileSender
from twisted.internet import reactor, endpoints, task, defer
from twisted.web.server import Site
from twisted.web import http
from twisted.web.client import URI
from twisted.web.resource import Resource, NoResource
from twisted.web.static import File
from twisted.web import server
from twisted.web.server import Session
from twisted.python.url import URL
from twisted.python.components import registerAdapter
from zope.interface import Interface, Attribute, implementer

# Autobahn provides websocket service under Twisted
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from autobahn.websocket.compress import *

# Specific functions to import from standard modules
from time import time, strftime, localtime
from pickle import loads
from binascii import b2a_hex as h
from os.path import getmtime

# Utilities from K0USY Group sister project
from dmr_utils3.utils import int_id, get_alias, try_download, mk_full_id_dict, bytes_4

# Configuration variables and constants
from config import *
from extracommand import *

# MYSQL stuff (pip install mysql-connector-python)
from mysql.connector import connect, Error
import pandas as pd

# support for xlsx files
import xlsxwriter

# SP2ONG - Increase the value if HBlink link break occurs
NetstringReceiver.MAX_LENGTH = 500000000

LOGINFO = False

# Opcodes for reporting protocol to HBlink
OPCODE = {
    'CONFIG_REQ': '\x00',
    'CONFIG_SND': '\x01',
    'BRIDGE_REQ': '\x02',
    'BRIDGE_SND': '\x03',
    'CONFIG_UPD': '\x04',
    'BRIDGE_UPD': '\x05',
    'LINK_EVENT': '\x06',
    'BRDG_EVENT': '\x07',
    }

# Global Variables:
CONFIG      = {}
CTABLE      = {'MASTERS': {}, 'PEERS': {}, 'OPENBRIDGES': {}, 'SETUP': {}}
BRIDGES     = {}
BTABLE      = {}
BTABLE['BRIDGES'] = {}
BRIDGES_RX  = ''
CONFIG_RX   = ''

LASTHEARDSIZE       = LAST_HEARD_SIZE
TRAFFICSIZE         = TRAFFIC_SIZE
CTABLEJ             = ""
MESSAGEJ            = []
SILENTJ             = True
VOICEJ              = False
LISTENERSJ          = []
CONTACTSJ           = []
BUTTONBAR_HTML      = ""

MOBILEPHONE         = False

# Define setup setings
CTABLE['SETUP']['LASTHEARD'] = LASTHEARD_INC

# TGID filter for lasheard
def get_tgidf():
    try:
        if len(TGID_ALLOWED) !=0:
            mylist = TGID_ALLOWED.replace(' ','').split(',')
        else:
            mylist = []
    except NameError:
       mylist = []

    return mylist

# OPB Filter for lastheard
def get_opbf():
   if len(OPB_FILTER) !=0:
       mylist = OPB_FILTER.replace(' ','').split(',')
   else:
       mylist = []

   return mylist

# For importing HTML templates
def get_template(_file):
    with open(_file, 'r') as html:
        return html.read()

# Alias string processor
def alias_string(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'CITY', 'STATE')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return alias

def alias_only(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'NAME')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)

        return alias
    else:    
        return ["", str(alias)]

def alias_short(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'NAME')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)

def alias_call(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)

def alias_tgid(_id, _dict):
    alias = get_alias(_id, _dict, 'NAME')
    if type(alias) == list:
        return str(alias[0])
    else:
        return str(alias)

# Return friendly elapsed time from time in seconds.
def since(_time):
    now = int(time())
    _time = now - int(_time)
    seconds = _time % 60
    minutes = int(_time/60) % 60
    hours = int(_time/60/60) % 24
    days = int(_time/60/60/24)
    if days:
        return '{}d {}h'.format(days, hours)
    elif hours:
        return '{}h {}m'.format(hours, minutes)
    elif minutes:
        return '{}m {}s'.format(minutes, seconds)
    else:
        return '{}s'.format(seconds)

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

def replaceSystemStrings(data):
    return data.replace("<<<site_logo>>>", sitelogo_html).replace("<<<system_name>>>", REPORT_NAME) \
        .replace("<<<button_bar>>>", BUTTONBAR_HTML) \
        .replace("<<<TGID_FILTER>>>", str(TGID_FILTER)) \
        .replace("<<<TGID_ORDER>>>", str(TGID_ORDER)) \
        .replace("<<<TGID_HILITE>>>", str(TGID_HILITE)) \
        .replace("<<<TGID_COLORS>>>", str(TGID_COLORS)) \
        .replace("<<<SOCKET_SERVER_PORT>>>", str(SOCKET_SERVER_PORT)) \
        .replace("<<<DISPLAY_LINES>>>", str(DISPLAY_LINES)) \
        .replace("<<<LAST_ACTIVE_TG>>>", str(LAST_ACTIVE_TG)) \
        .replace("<<<LAST_ACTIVE_SIZE>>>", str(LAST_ACTIVE_SIZE)) \
        .replace("<<<DYNAMIC_TG>>>", str(DYNAMIC_TG)) \
        .replace("<<<TGID_BEACONS>>>", str(TGID_BEACONS)) \
        .replace("<<<MOBILE>>>", str(MOBILEPHONE)) \
        .replace("<<<HIDE_DMRID>>>", str(HIDE_DMRID))#.replace("class=\"theme-dark\"", "class=\"theme-light\"")

def logMySQL(_data):
    if SQL_LOG == True:
        #logging.info('MYSQL DATA: {}'.format(_data))

        try:
            with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS, database=SQL_DATABASE) as connection:
                with connection.cursor(buffered=True) as cursor:
                    p = _data.split(",")
                    REPORT_DATE       = p[0][0:10].strip()
                    REPORT_TIME       = p[0][11:19].strip()
                    REPORT_DELAY      = p[1].strip()
                    REPORT_TYPE       = p[2][6:].strip()
                    REPORT_PACKET     = p[3].strip()
                    REPORT_SYS        = p[4].strip()
                    REPORT_SRC_ID     = p[5].strip()
                    REPORT_NETID_NAME = p[6].strip()
                    REPORT_TS         = p[7][2:3].strip()
                    REPORT_TGID       = p[8][2:].strip()
                    REPORT_ALIAS      = p[9].strip()
                    REPORT_DMRID      = p[10].strip()
                    REPORT_CALLSIGN   = p[11].strip()
                    if len(p) == 12:
                        REPORT_NAME = "---"
                    else:
                        REPORT_NAME = p[12].strip()

                    logging.info(_data)

                    # log packet for lastlog
                    cursor.execute("INSERT INTO log (date,time,type,packet,sys,srcid,netidname,ts,tgid,alias,dmrid,callsign,name,delay) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (REPORT_DATE, REPORT_TIME, REPORT_TYPE, REPORT_PACKET, REPORT_SYS, REPORT_SRC_ID, REPORT_NETID_NAME, REPORT_TS, REPORT_TGID, REPORT_ALIAS, REPORT_DMRID, REPORT_CALLSIGN, REPORT_NAME, REPORT_DELAY))

                    # update usrp last seen
                    if REPORT_PACKET == "END":
                        cursor.execute("UPDATE usrp SET logdate='{}', logtime='{}' WHERE id='{}'".format(REPORT_DATE, REPORT_TIME, REPORT_DMRID))

                    connection.commit()

                    cursor.close()

                connection.close()

        except Error as e:
            if LOGINFO == True:
                logging.info('MYSQL ERROR: {}'.format(e))

private_secret = os.urandom(64)

def generateRandomSessionKey():
    session_key = binascii.hexlify(os.urandom(16))
    return session_key

def initIpMap():
    if SQL_LOG == True:
        try:
            with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS, database=SQL_DATABASE) as connection:
                with connection.cursor(buffered=True) as cursor:
                    # get tables list
                    tableNotFound = True
                    cursor.execute("SHOW TABLES")
                    
                    # check if our table is already there
                    for (table,) in cursor:
                        if (table == "ipmap"):
                            tableNotFound = False
                            break

                    # create table if does not exist
                    if tableNotFound == True:
                        print("ipmap table not found, creating a new empty table")
                        cursor.execute("CREATE TABLE ipmap ( \
                                            ip VARCHAR(16), \
                                            port VARCHAR(8), \
                                            callsign VARCHAR(16), \
                                            netid VARCHAR(16), \
                                            PRIMARY KEY (ip, port) \
                                            )")

                    cursor.close()

                connection.close()
        except Error as e:
            if LOGINFO == True:
                logging.info('MYSQL ERROR: {}'.format(e))
    else:
        # create file if does not exist
        if not os.path.exists(LOG_PATH + "ipmap.json"):
            logging.info("Creating empty " + LOG_PATH + "ipmap.json")
            with open(LOG_PATH + "ipmap.json", 'w') as outfile:
                json.dump({ "IPMAP" : [] }, outfile)

def mapIpAdresses():
    global LISTENERSJ

    try:
        _rows = []
        LISTENERSJ = []

        for system in CTABLE['MASTERS']:
            for peer in CTABLE['MASTERS'][system]['PEERS']:
                record = CTABLE['MASTERS'][system]['PEERS'][peer]
                if record["CALLSIGN"] and record["IP"] and record["PORT"]:
                    _callsign = record["CALLSIGN"].strip()
                    _netid = str(peer)
                    _ip = record["IP"].strip()
                    _port = str(record["PORT"])
                    _rows.append((_ip, _port, _callsign, _netid))

        if len(_rows) > 0:
            if SQL_LOG == True:
                with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS, database=SQL_DATABASE) as connection:
                    with connection.cursor(buffered=True) as cursor:
                        cursor.executemany("INSERT IGNORE INTO ipmap (ip,port,callsign,netid) VALUES (%s,%s,%s,%s)", _rows)
                        connection.commit()

                        if len(dashboard_server.clients) > 0:
                            _query = ""

                            for client in dashboard_server.clients:
                                _p = client.peer.split(":")
                                if len(_query) > 0:
                                    _query = _query + " or "
                                _query = _query + "ip='"+_p[1] + "'"

                            # print("select * from ipmap where " + _query)
                            cursor.execute("select * from ipmap where " + _query)

                            listeners = cursor.fetchall()

                            for row in listeners:
                                LISTENERSJ.append({ 'CALLSIGN': row[2], 'IP': row[0], 'PORT': row[1], 'NETID': row[3] })

                            # print(LISTENERSJ)

                        cursor.close()
                    connection.close()
            else:
                with open(LOG_PATH + "ipmap.json", 'r+') as file:
                    ipmap = json.load(file)
                    updated = False
                    # print("rows size = " + str(len(_rows)))

                    for row in _rows:
                        found = False
                        _callsign = row[2].strip()
                        _netid = row[3]
                        _ip = row[0].strip()
                        _port = row[1]

                        if len(ipmap["IPMAP"]) > 0:
                            # print("callsign = " + _callsign + " ip = " + _ip)
                            for record in ipmap["IPMAP"]:
                                if _ip == record["IP"]:
                                    found = True
                                    break

                        if not found:
                            # print("callsign = " + _callsign + " not found ip = " + _ip)
                            updated = True
                            ipmap["IPMAP"].append({ 'CALLSIGN': _callsign, 'IP': _ip, 'PORT': _port, 'NETID': _netid })

                    if updated:
                        file.seek(0)
                        json.dump({ "IPMAP": ipmap["IPMAP"] }, file, indent=4)
                        file.truncate()

                    for client in dashboard_server.clients:
                        _p = client.peer.split(":")
                        for record in ipmap["IPMAP"]:
                            # print("clientip = " + _p[1] + " record['IP'] = " + record["IP"])
                            if _p[1] == record["IP"]:
                                # print(record)
                                LISTENERSJ.append(record)

    except Error as e:
        #if LOGINFO == True:
        logging.info('MYSQL ERROR: {}'.format(e))

##################################################
# Cleaning entries in tables - Timeout (5 min) 
#
def cleanTE():
    timeout = datetime.datetime.now().timestamp()

    for system in CTABLE['MASTERS']:
        for peer in CTABLE['MASTERS'][system]['PEERS']:
            for timeS in range(1,3):
              if CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TS']:
                ts = CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TIMEOUT']
                td = ts - timeout if ts > timeout else timeout - ts
                td = int(round(abs((td)) / 60))
                if td > 3:
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TS'] = False
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TXRX'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['TYPE'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['SUB'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['SRC'] = ''
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeS]['DEST'] = ''

    for system in CTABLE['PEERS']:
        for timeS in range(1,3):
            if CTABLE['PEERS'][system][timeS]['TS']:
                ts = CTABLE['PEERS'][system][timeS]['TIMEOUT']
                td = ts - timeout if ts > timeout else timeout - ts
                td = int(round(abs((td)) / 60))
                if td > 3:
                    CTABLE['PEERS'][system][timeS]['TS'] = False
                    CTABLE['PEERS'][system][timeS]['TXRX'] = ''
                    CTABLE['PEERS'][system][timeS]['TYPE'] = ''
                    CTABLE['PEERS'][system][timeS]['SUB'] = ''
                    CTABLE['PEERS'][system][timeS]['SRC'] = ''
                    CTABLE['PEERS'][system][timeS]['DEST'] = ''

    for system in CTABLE['OPENBRIDGES']:
        for streamId in list(CTABLE['OPENBRIDGES'][system]['STREAMS']):
            ts = CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId][3]
            td = ts - timeout if ts > timeout else timeout - ts
            td = int(round(abs((td)) / 60))
            if td > 3:
                 del CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId]

                    
def add_hb_peer(_peer_conf, _ctable_loc, _peer):
    _ctable_loc[int_id(_peer)] = {}
    _ctable_peer = _ctable_loc[int_id(_peer)]

    # if the Frequency is 000.xxx assume it's not an RF peer, otherwise format the text fields
    # (9 char, but we are just software)  see https://wiki.brandmeister.network/index.php/Homebrew/example/php2
    
    if _peer_conf['TX_FREQ'].strip().isdigit() and _peer_conf['RX_FREQ'].strip().isdigit() and str(type(_peer_conf['TX_FREQ'])).find("bytes") != -1 and str(type(_peer_conf['RX_FREQ'])).find("bytes") != -1:
        if _peer_conf['TX_FREQ'][:3] == b'000' or _peer_conf['RX_FREQ'][:3] == b'000':
            _ctable_peer['TX_FREQ'] = 'N/A'
            _ctable_peer['RX_FREQ'] = 'N/A'
        else:
            _ctable_peer['TX_FREQ'] = _peer_conf['TX_FREQ'][:3].decode('utf-8') + '.' + _peer_conf['TX_FREQ'][3:7].decode('utf-8') + ' MHz'
            _ctable_peer['RX_FREQ'] = _peer_conf['RX_FREQ'][:3].decode('utf-8') + '.' + _peer_conf['RX_FREQ'][3:7].decode('utf-8') + ' MHz'
    else:
        _ctable_peer['TX_FREQ'] = 'N/A'
        _ctable_peer['RX_FREQ'] = 'N/A'

    # timeslots are kinda complicated too. 0 = none, 1 or 2 mean that one slot, 3 is both, and anything else it considered DMO
    # Slots (0, 1=1, 2=2, 1&2=3 Duplex, 4=Simplex) see https://wiki.brandmeister.network/index.php/Homebrew/example/php2
    
    if (_peer_conf['SLOTS'] == b'0'):
        _ctable_peer['SLOTS'] = 'NONE'
    elif (_peer_conf['SLOTS'] == b'1' or _peer_conf['SLOTS'] == b'2'):
        _ctable_peer['SLOTS'] = _peer_conf['SLOTS'].decode('utf-8')
    elif (_peer_conf['SLOTS'] == b'3'):
        _ctable_peer['SLOTS'] = 'Duplex'
    else:
        _ctable_peer['SLOTS'] = 'Simplex'

    # Simple translation items
    if str(type(_peer_conf['PACKAGE_ID'])).find("bytes") != -1:
       _ctable_peer['PACKAGE_ID'] = _peer_conf['PACKAGE_ID'].decode('utf-8').strip()
    else:
       _ctable_peer['PACKAGE_ID'] = _peer_conf['PACKAGE_ID']

    if str(type(_peer_conf['SOFTWARE_ID'])).find("bytes") != -1:
       _ctable_peer['SOFTWARE_ID'] = _peer_conf['SOFTWARE_ID'].decode('utf-8').strip()
    else:
       _ctable_peer['SOFTWARE_ID'] = _peer_conf['SOFTWARE_ID']

    if str(type(_peer_conf['LOCATION'])).find("bytes") != -1:
       _ctable_peer['LOCATION'] = _peer_conf['LOCATION'].decode('utf-8').strip()
    else:
       _ctable_peer['LOCATION'] = _peer_conf['LOCATION']

    if str(type(_peer_conf['CALLSIGN'])).find("bytes") != -1:
       _ctable_peer['CALLSIGN'] = _peer_conf['CALLSIGN'].decode('utf-8').strip()
    else:
       _ctable_peer['CALLSIGN'] = _peer_conf['CALLSIGN']
    
    if str(type(_peer_conf['COLORCODE'])).find("bytes") != -1:
        _ctable_peer['COLORCODE'] = _peer_conf['COLORCODE'].decode('utf-8')
    else:
        _ctable_peer['COLORCODE'] = _peer_conf['COLORCODE']

    if str(type(_peer_conf['CALLSIGN'])).find("bytes") != -1:
        _ctable_peer['CALLSIGN'] = _peer_conf['CALLSIGN'].decode('utf-8')
    else:
        _ctable_peer['CALLSIGN'] = _peer_conf['CALLSIGN']

    _ctable_peer['CONNECTION'] = _peer_conf['CONNECTION']
    _ctable_peer['CONNECTED'] = since(_peer_conf['CONNECTED'])
    #_ctable_peer['ONLINE'] = str(_peer_conf['CONNECTED'])
    _ctable_peer['IP'] = _peer_conf['IP']
    _ctable_peer['PORT'] = _peer_conf['PORT']
    #_ctable_peer['LAST_PING'] = _peer_conf['LAST_PING']

    # SLOT 1&2 - for real-time montior: make the structure for later use
    for ts in range(1,3):
        _ctable_peer[ts]= {}
        _ctable_peer[ts]['TS'] = ''
        _ctable_peer[ts]['TYPE'] = ''
        _ctable_peer[ts]['SUB'] = ''
        _ctable_peer[ts]['SRC'] = ''
        _ctable_peer[ts]['DEST'] = ''
        _ctable_peer[ts]['TXRX'] = ''

######################################################################
#
# Build the HBlink connections table
#

def build_hblink_table(_config, _stats_table):
    for _hbp, _hbp_data in list(_config.items()):
        if _hbp_data['ENABLED'] == True:

            # Process Master Systems
            if _hbp_data['MODE'] == 'MASTER':
                _stats_table['MASTERS'][_hbp] = {}
                if _hbp_data['REPEAT']:
                    _stats_table['MASTERS'][_hbp]['REPEAT'] = "repeat"
                else:
                    _stats_table['MASTERS'][_hbp]['REPEAT'] = "isolate"
                _stats_table['MASTERS'][_hbp]['PEERS'] = {}
                for _peer in _hbp_data['PEERS']:
                    add_hb_peer(_hbp_data['PEERS'][_peer], _stats_table['MASTERS'][_hbp]['PEERS'], _peer)

            # Proccess Peer Systems
            elif (_hbp_data['MODE'] == 'XLXPEER' or _hbp_data['MODE'] == 'PEER') and HOMEBREW_INC:
                _stats_table['PEERS'][_hbp] = {}
                _stats_table['PEERS'][_hbp]['MODE'] = _hbp_data['MODE']

                if str(type(_hbp_data['LOCATION'])).find("bytes") != -1:
                     _stats_table['PEERS'][_hbp]['LOCATION'] = _hbp_data['LOCATION'].decode('utf-8').strip()
                else:
                     _stats_table['PEERS'][_hbp]['LOCATION'] = _hbp_data['LOCATION']

                if str(type(_hbp_data['CALLSIGN'])).find("bytes") != -1:
                     _stats_table['PEERS'][_hbp]['CALLSIGN'] = _hbp_data['CALLSIGN'].decode('utf-8').strip()
                else:
                     _stats_table['PEERS'][_hbp]['CALLSIGN'] = _hbp_data['CALLSIGN']

                _stats_table['PEERS'][_hbp]['RADIO_ID'] = int_id(_hbp_data['RADIO_ID'])
                _stats_table['PEERS'][_hbp]['MASTER_IP'] = _hbp_data['MASTER_IP']
                _stats_table['PEERS'][_hbp]['MASTER_PORT'] = _hbp_data['MASTER_PORT']
                _stats_table['PEERS'][_hbp]['STATS'] = {}

                if _stats_table['PEERS'][_hbp]['MODE'] == 'XLXPEER': 
                    _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _hbp_data['XLXSTATS']['CONNECTION']

                    if _hbp_data['XLXSTATS']['CONNECTION'] == "YES":
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_hbp_data['XLXSTATS']['CONNECTED'])
                        #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = str(_hbp_data['XLXSTATS']['CONNECTED'])
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _hbp_data['XLXSTATS']['PINGS_SENT']
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _hbp_data['XLXSTATS']['PINGS_ACKD']
                    else:
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                        #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = "0"
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
                else:
                    _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _hbp_data['STATS']['CONNECTION']

                    if _hbp_data['STATS']['CONNECTION'] == "YES":
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_hbp_data['STATS']['CONNECTED'])
                        #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = str(_hbp_data['STATS']['CONNECTED'])
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _hbp_data['STATS']['PINGS_SENT']
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _hbp_data['STATS']['PINGS_ACKD']
                    else:
                        _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                        #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = "0"
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                        _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0

                if _hbp_data['SLOTS'] == b'0':
                    _stats_table['PEERS'][_hbp]['SLOTS'] = 'NONE'
                elif _hbp_data['SLOTS'] == b'1' or _hbp_data['SLOTS'] == b'2':
                    _stats_table['PEERS'][_hbp]['SLOTS'] = _hbp_data['SLOTS'].decode('utf-8')
                elif _hbp_data['SLOTS'] == b'3':
                    _stats_table['PEERS'][_hbp]['SLOTS'] = '1&2'
                else:
                    _stats_table['PEERS'][_hbp]['SLOTS'] = 'DMO'

                # SLOT 1&2 - for real-time montior: make the structure for later use
                for ts in range(1,3):
                    _stats_table['PEERS'][_hbp][ts]= {}
                    _stats_table['PEERS'][_hbp][ts]['TXRX'] = ''
                    _stats_table['PEERS'][_hbp][ts]['TS'] = ''
                    _stats_table['PEERS'][_hbp][ts]['TYPE'] = ''
                    _stats_table['PEERS'][_hbp][ts]['SUB'] = ''
                    _stats_table['PEERS'][_hbp][ts]['SRC'] = ''
                    _stats_table['PEERS'][_hbp][ts]['DEST'] = ''

            # Process OpenBridge systems
            elif _hbp_data['MODE'] == 'OPENBRIDGE':
                _stats_table['OPENBRIDGES'][_hbp] = {}
                _stats_table['OPENBRIDGES'][_hbp]['NETWORK_ID'] = int_id(_hbp_data['NETWORK_ID'])
                _stats_table['OPENBRIDGES'][_hbp]['TARGET_IP'] = _hbp_data['TARGET_IP']
                _stats_table['OPENBRIDGES'][_hbp]['TARGET_PORT'] = _hbp_data['TARGET_PORT']
                _stats_table['OPENBRIDGES'][_hbp]['STREAMS'] = {}

    #return(_stats_table)

def update_hblink_table(_config, _stats_table):
    # Is there a system in HBlink's config monitor doesn't know about?
    for _hbp in _config:
        if _config[_hbp]['MODE'] == 'MASTER':
            for _peer in _config[_hbp]['PEERS']:
                if int_id(_peer) not in _stats_table['MASTERS'][_hbp]['PEERS'] and _config[_hbp]['PEERS'][_peer]['CONNECTION'] == 'YES':
                    logger.info('Adding peer to CTABLE that has registered: %s', int_id(_peer))
                    add_hb_peer(_config[_hbp]['PEERS'][_peer], _stats_table['MASTERS'][_hbp]['PEERS'], _peer)

    # Is there a system in monitor that's been removed from HBlink's config?
    for _hbp in _stats_table['MASTERS']:
        remove_list = []
        if _config[_hbp]['MODE'] == 'MASTER':
            for _peer in _stats_table['MASTERS'][_hbp]['PEERS']:
                if bytes_4(_peer) not in _config[_hbp]['PEERS']:
                    remove_list.append(_peer)

            for _peer in remove_list:
                logger.info('Deleting stats peer not in hblink config: %s', _peer)
                del (_stats_table['MASTERS'][_hbp]['PEERS'][_peer])

    # Update connection time
    for _hbp in _stats_table['MASTERS']:
        for _peer in _stats_table['MASTERS'][_hbp]['PEERS']:
            if bytes_4(_peer) in _config[_hbp]['PEERS']:
                _stats_table['MASTERS'][_hbp]['PEERS'][_peer]['CONNECTED'] = since(_config[_hbp]['PEERS'][bytes_4(_peer)]['CONNECTED'])

    for _hbp in _stats_table['PEERS']:
        if _stats_table['PEERS'][_hbp]['MODE'] == 'XLXPEER':
            if _config[_hbp]['XLXSTATS']['CONNECTION'] == "YES":
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_config[_hbp]['XLXSTATS']['CONNECTED'])
                #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = str(_config[_hbp]['XLXSTATS']['ONLINE'])
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['XLXSTATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _config[_hbp]['XLXSTATS']['PINGS_SENT']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _config[_hbp]['XLXSTATS']['PINGS_ACKD']
            else:
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = "0"
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['XLXSTATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
        else:
            if _config[_hbp]['STATS']['CONNECTION'] == "YES":
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = since(_config[_hbp]['STATS']['CONNECTED'])
                #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = str(_config[_hbp]['STATS']['ONLINE'])
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['STATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = _config[_hbp]['STATS']['PINGS_SENT']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = _config[_hbp]['STATS']['PINGS_ACKD']
            else:
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTED'] = "--   --"
                #_stats_table['PEERS'][_hbp]['STATS']['ONLINE'] = "0"
                _stats_table['PEERS'][_hbp]['STATS']['CONNECTION'] = _config[_hbp]['STATS']['CONNECTION']
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_SENT'] = 0
                _stats_table['PEERS'][_hbp]['STATS']['PINGS_ACKD'] = 0
    
    cleanTE()
    build_stats()

######################################################################
#
# CONFBRIDGE TABLE FUNCTIONS
#

def build_bridge_table(_bridges):
    _stats_table = {}
    _now = time()
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(_now))

    for _bridge, _bridge_data in list(_bridges.items()):
        _stats_table[_bridge] = {}

        for system in _bridges[_bridge]:
            _stats_table[_bridge][system['SYSTEM']] = {}
            _stats_table[_bridge][system['SYSTEM']]['TS'] = system['TS']
            _stats_table[_bridge][system['SYSTEM']]['TGID'] = int_id(system['TGID'])

            #_stats_table[_bridge][system['SYSTEM']]['TS']['TXRX'] = ''

            if system['TO_TYPE'] == 'ON' or system['TO_TYPE'] == 'OFF':
                if system['TIMER'] - _now > 0:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = int(system['TIMER'] - _now)
                else:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'Expired'
                if system['TO_TYPE'] == 'ON':
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Disconnect'
                else:
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Connect'
            else:
                _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'N/A'
                _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'None'

            if system['ACTIVE'] == True:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Connected'
            elif system['ACTIVE'] == False:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Disconnected'

            for i in range(len(system['ON'])):
                system['ON'][i] = str(int_id(system['ON'][i]))

            _stats_table[_bridge][system['SYSTEM']]['TRIG_ON'] = ', '.join(system['ON'])

            for i in range(len(system['OFF'])):
                system['OFF'][i] = str(int_id(system['OFF'][i]))

            _stats_table[_bridge][system['SYSTEM']]['TRIG_OFF'] = ', '.join(system['OFF'])
    return _stats_table

######################################################################
#
# BUILD HBlink AND CONFBRIDGE TABLES FROM CONFIG/BRIDGES DICTS
#          THIS CURRENTLY IS A TIMED CALL
#
build_time = time()
def build_stats():
    global build_time, LISTENERSJ
    now = time()

    if (now > build_time + 0.5) and ('dashboard_server' in locals() or 'dashboard_server' in globals()):
        for client in dashboard_server.clients:
            if CONFIG:            
                if client.page != "ccs7":
                    if client.page == "dashboard":
                        CTABLEJ = { 'CTABLE' : CTABLE, 'EMPTY_MASTERS' : EMPTY_MASTERS, 'BIGEARS': str(len(dashboard_server.clients)), 'LISTENERS': LISTENERSJ }
                        client.sendMessage(json.dumps(CTABLEJ, ensure_ascii = False).encode('utf-8'))
                    elif client.page != "bridges":
                        CTABLEJ = { 'BIGEARS': str(len(dashboard_server.clients)), 'LISTENERS': LISTENERSJ }
                        client.sendMessage(json.dumps(CTABLEJ, ensure_ascii = False).encode('utf-8'))
        
            if BRIDGES and BRIDGES_INC and client.page == "bridges":
                client.sendMessage(json.dumps({ "BTABLE": { 'BRIDGES': BTABLE['BRIDGES'] }}, ensure_ascii = False).encode('utf-8'))
            
        mapIpAdresses()

        build_time = now

def timeout_clients():
    now = time()
    try:
        for client in dashboard_server.clients:
            if dashboard_server.clients[client] + CLIENT_TIMEOUT < now:
                logger.info('TIMEOUT: disconnecting client %s', dashboard_server.clients[client])
                try:
                    dashboard.sendClose(client)
                except Exception as e:
                    logger.error('Exception caught parsing client timeout %s', e)
    except:
        logger.info('CLIENT TIMEOUT: List does not exist, skipping. If this message persists, contact the developer')


def rts_update(p):
    callType = p[0]
    action = p[1]
    trx = p[2]
    system = p[3]
    streamId = p[4]
    sourcePeer = int(p[5])
    sourceSub = int(p[6])
    timeSlot = int(p[7])
    destination = int(p[8])
    timeout = datetime.datetime.now().timestamp()
    
    if system in CTABLE['MASTERS']:
        for peer in CTABLE['MASTERS'][system]['PEERS']:
            if action == 'START':
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TIMEOUT'] = timeout
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TS'] = True
                
                if sourcePeer in (None, '') or peer in (None, ''):
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TXRX'] = ''
                else:
                    CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TXRX'] = "TX" if (sourcePeer == peer) else "RX"

                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TYPE'] = callType
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SRC'] = peer
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SUB'] = '{} ({})'.format(alias_short(sourceSub, subscriber_ids), sourceSub)
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['DEST'] = '{} ({})'.format(alias_tgid(destination, talkgroup_ids), destination)
              
            if action == 'END':
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TS'] = False
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TXRX'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['TYPE'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SUB'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['SRC'] = ''
                CTABLE['MASTERS'][system]['PEERS'][peer][timeSlot]['DEST'] = ''

                # deal with Extracommands etc..
                rts_update_extra(destination)

    if system in CTABLE['OPENBRIDGES']:
        if action == 'START':
            CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId] = (trx, alias_call(sourceSub, subscriber_ids),'TG{}'.format(destination),timeout)

        if action == 'END':
            if streamId in CTABLE['OPENBRIDGES'][system]['STREAMS']:
                del CTABLE['OPENBRIDGES'][system]['STREAMS'][streamId]

    if system in CTABLE['PEERS']:
        if action == 'START':
            CTABLE['PEERS'][system][timeSlot]['TIMEOUT'] = timeout
            CTABLE['PEERS'][system][timeSlot]['TS'] = True
            CTABLE['PEERS'][system][timeSlot]['SUB'] = '{} ({})'.format(alias_short(sourceSub, subscriber_ids), sourceSub)
            CTABLE['PEERS'][system][timeSlot]['SRC'] = sourcePeer
            CTABLE['PEERS'][system][timeSlot]['DEST'] = '{} ({})'.format(alias_tgid(destination, talkgroup_ids), destination)

            if not sourcePeer or not sourceSub or not destination:
                CTABLE['PEERS'][system][timeSlot]['TXRX'] = ''
            else:
                CTABLE['PEERS'][system][timeSlot]['TXRX'] = trx

        if action == 'END':
            CTABLE['PEERS'][system][timeSlot]['TS'] = False
            CTABLE['PEERS'][system][timeSlot]['TYPE'] = ''
            CTABLE['PEERS'][system][timeSlot]['SUB'] = ''
            CTABLE['PEERS'][system][timeSlot]['SRC'] = ''
            CTABLE['PEERS'][system][timeSlot]['DEST'] = ''                                                  
            CTABLE['PEERS'][system][timeSlot]['TXRX'] = ''

    build_stats()


def createlocalUsersFromSql():
    try:
        with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS,database=SQL_DATABASE) as connection:
            with connection.cursor(buffered=True) as cursor:
                # cursor.execute('select * from local_subscribers where callsign like("FS%") or callsign like("BS%") or callsign like("FI%") and callsign not like "%0";')
                cursor.execute('select * from local_subscribers where (remarks="SHIELD" or remarks="FRS") and callsign not like "%0";')
                subscribers = cursor.fetchall()

                SUBSCRIBERSJ = []

                for row in subscribers:
                    SUBSCRIBERSJ.append({
                        'FNAME':    row[0],
                        'NAME':     row[1], 
                        'SURNAME':  row[2], 
                        'CITY':     row[3],
                        'STATE':    row[4],
                        'COUNTRY':  row[5],
                        'CALLSIGN': row[6],
                        'ID':       row[7],
                        'REMARKS':  row[8]
                    })


                cursor.close()    
                connection.close()
                return SUBSCRIBERSJ

    except Error as e:
        print("Error {} ", e)

######################################################################
# 
# LOG+
#     

def createlogLastFromSql(EndPacketOnly):
    try:
        with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS,database=SQL_DATABASE) as connection:
            with connection.cursor(buffered=True) as cursor:
                if EndPacketOnly:
                    cursor.execute('select * from log where tgid in ('+TGID_ORDER+') and packet="END" order by concat_ws(date, " ", time) desc limit ' + str(LASTHEARDSIZE) + ';')
                else:
                    cursor.execute('select * from log where tgid in ('+TGID_ORDER+') order by concat_ws(date, " ", time) desc limit ' + str(LASTHEARDSIZE) + ';')
                    
                logs = cursor.fetchall()

                MESSAGEJ = []

                for row in logs:
                    REPORT_DATE     = row[1]
                    REPORT_TIME     = row[2]
                    REPORT_DELAY    = row[14]
                    REPORT_INFRA    = row[5]

                    REPORT_PACKET   = row[4]

                    REPORT_SRC_ID   = row[6]
                    REPORT_DMRID    = row[11]

                    REPORT_TS       = row[8]
                    REPORT_TGID     = row[9]
                    REPORT_LOGP     = row[10]

                    REPORT_NETID    = row[7]

                    REPORT_CALLSIGN = row[12]

                    REPORT_FNAME    = row[13]

                    MESSAGEJ.append({
                        'DATE': REPORT_DATE,
                        'TIME': REPORT_TIME,
                        'TS': REPORT_TS,
                        'PACKET': REPORT_PACKET, 
                        'CALLSIGN': REPORT_CALLSIGN,
                        'DMRID': REPORT_DMRID,
                        'NAME': REPORT_FNAME,
                        'TGID': REPORT_TGID,
                        'ALIAS': REPORT_LOGP,
                        'DELAY': REPORT_DELAY,
                        'SYS': REPORT_INFRA,
                        'SRC_ID':  REPORT_NETID })


                cursor.close()    
                connection.close()
                return MESSAGEJ

    except Error as e:
        print("Error {} ", e)

def createLogTableJson():
    MESSAGEJ = []

    with open(LOG_PATH + "lastheard.log", "r") as lastheard:
        subset = islice(reversed(list(csv.reader(lastheard))), 2000)
        for row in subset:

            REPORT_TGID = row[8][2:]

            if (len(tgid_allowed) == 0 or REPORT_TGID in tgid_allowed):
                REPORT_DATE     = row[0]
                REPORT_DELAY    = row[1]
                REPORT_INFRA    = row[4]

                REPORT_SRC_ID   = row[5]
                REPORT_DMRID    = row[10]

                REPORT_TS       = row[7]
                REPORT_LOGP     = row[9]

                REPORT_NETID    = row[6]

                REPORT_CALLSIGN = row[11]

                if len(row) < 13:
                    row.append("---")

                REPORT_FNAME     = row[12]

                MESSAGEJ.append({ 
                    'DATE': REPORT_DATE[:10], 
                    'TIME': REPORT_DATE[11:16], 
                    'TS': REPORT_TS[2:], 
                    'CALLSIGN': REPORT_CALLSIGN, 
                    'DMRID': REPORT_DMRID, 
                    'NAME': REPORT_FNAME, 
                    'TGID': REPORT_TGID, 
                    'ALIAS': REPORT_LOGP, 
                    'DELAY': REPORT_DELAY,
                    'SYS': REPORT_INFRA, 
                    'SRC_ID':  REPORT_NETID })

    return MESSAGEJ

def tableToExcel(tableName):
    if SQL_LOG == True:
        try:
            with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS, database=SQL_DATABASE) as connection:
                with connection.cursor(buffered=True) as cursor:
                    # read updated usrp table sorted by tph
                    cursor.execute("select * from " + tableName + ";")
                    df_data = pd.DataFrame(list(cursor.fetchall()), columns = [desc[0] for desc in cursor.description])

                    with pd.ExcelWriter("/tmp/" + tableName + ".xlsx", engine="xlsxwriter") as writer:
                        df_data.to_excel(writer, sheet_name = tableName)

                    cursor.close()    
                connection.close()

        except Error as e:
            if LOGINFO == True:
                logging.info('MYSQL ERROR: {}'.format(e))

# "radioid", "https://database.radioid.net/static/users.json");
# "Francophonie", "http://francophonie.link/local_subscriber_ids.json");
def fetchRemoteUsersFiles(fileurl):
    if fileurl != "":
        logging.info('requesting: %s', fileurl)

        filename = str(fileurl.rsplit('/', 1)[-1])
        filepath = PATH + "assets/" + filename

        # keep shield file always updated
        if filename != "local_subscriber_ids.json":
            if os.path.exists(filepath):
                _time = int(time()) - int(creation_date(filepath))
                # check if file needs new download from remote
                if int(_time/60/60/24) < 7:
                    return filename

        # file is older than 7 days, download 
        with urllib.request.urlopen(fileurl) as url:
            with open(filepath, 'w') as users_json:
                users_json.write(url.read().decode("utf-8"))
                return filename

    return ""

def getLastHeardFromSQL():
    try:
        with connect(host=SQL_HOST, user=SQL_USER, password=SQL_PASS,database=SQL_DATABASE) as connection:
            with connection.cursor(buffered=True) as cursor:                
                cursor.execute('select * from log where tgid in ('+TGID_ORDER+') and packet="END" order by concat_ws(date, " ", time) desc limit ' + str(LASTHEARDSIZE) + ';')
                logs = cursor.fetchall()

                MESSAGEJ = []

                for row in logs:
                    REPORT_DATE     = row[1]
                    REPORT_TIME     = row[2]
                    REPORT_DELAY    = row[14]
                    REPORT_INFRA    = row[5]

                    REPORT_SRC_ID   = row[6]
                    REPORT_DMRID    = row[11]

                    REPORT_TS       = row[8]
                    REPORT_TGID     = row[9]
                    REPORT_LOGP     = row[10]

                    REPORT_NETID    = row[7]

                    REPORT_CALLSIGN = row[12]

                    REPORT_FNAME     = row[13]

                    MESSAGEJ.append({
                        'DATE': REPORT_DATE, 
                        'TIME': REPORT_TIME, 
                        'TS': REPORT_TS, 
                        'CALLSIGN': REPORT_CALLSIGN, 
                        'DMRID': REPORT_DMRID, 
                        'NAME': REPORT_FNAME, 
                        'TGID': REPORT_TGID, 
                        'ALIAS': REPORT_LOGP, 
                        'DELAY': REPORT_DELAY,
                        'SYS': REPORT_INFRA, 
                        'SRC_ID':  REPORT_NETID })

                cursor.close()    
                connection.close()
                return MESSAGEJ

    except Error as e:
        print("Error {} ", e)

######################################################################
#
# PROCESS INCOMING MESSAGES AND TAKE THE CORRECT ACTION DEPENING ON
#    THE OPCODE
#
def process_message(_bmessage):
    global CTABLE, CONFIG, BRIDGES, CONFIG_RX, BRIDGES_RX, MESSAGEJ
    _message = _bmessage.decode('utf-8', 'ignore')
    opcode = _message[:1]
    _now = strftime('%Y-%m-%d %H:%M:%S %Z', localtime(time()))

    start = ptime.perf_counter()

    if opcode == OPCODE['CONFIG_SND']:
        logging.debug('got CONFIG_SND opcode')
        CONFIG = load_dictionary(_bmessage)
        CONFIG_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))

        if CTABLE['MASTERS']:
            update_hblink_table(CONFIG, CTABLE)
        else:
            build_hblink_table(CONFIG, CTABLE)

    elif opcode == OPCODE['BRIDGE_SND']:
        logging.debug('got BRIDGE_SND opcode')
        BRIDGES = load_dictionary(_bmessage)
        BRIDGES_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        if BRIDGES_INC:
           BTABLE['BRIDGES'] = build_bridge_table(BRIDGES)

    elif opcode == OPCODE['LINK_EVENT']:
        logging.info('LINK_EVENT Received: {}'.format(repr(_message[1:])))

    elif opcode == OPCODE['BRDG_EVENT']:
        if LOGINFO == True:
            logging.info('BRIDGE EVENT: {}'.format(repr(_message[1:])))
        
        p = _message[1:].split(",")
        rts_update(p)
        opbfilter = get_opbf()

        REPORT_TYPE     = p[0]
        REPORT_RXTX     = p[2]
        REPORT_SRC_ID   = p[5]
        REPORT_TGID     = p[8]

        if (len(tgid_allowed) == 0 or REPORT_TGID in tgid_allowed) and REPORT_TYPE == 'GROUP VOICE' and REPORT_RXTX != 'TX' and REPORT_SRC_ID not in opbfilter:
            REPORT_DATE     = _now[0:10]
            REPORT_TIME     = _now[11:19]
            REPORT_PACKET   = p[1]
            REPORT_SYS      = p[3]
            REPORT_DMRID    = p[6]
            REPORT_TS       = p[7]
            REPORT_ALIAS    = alias_tgid(int(REPORT_TGID), talkgroup_ids)
            REPORT_CALLSIGN = alias_only(int(REPORT_DMRID), subscriber_ids)[0].strip()
            REPORT_FNAME    = alias_only(int(REPORT_DMRID), subscriber_ids)[1].strip()
            REPORT_BOTH     = alias_short(int(REPORT_DMRID), subscriber_ids)
            jsonStr = {}

            if REPORT_PACKET == 'END':
                REPORT_DELAY    = int(float(p[9]))

                # read saved history
                with open(LOG_PATH + "lastheard.json", 'r+') as file:
                    traffic = json.load(file)
                    
                    # clear array
                    MESSAGEJ = []

                    # remove all previous START packet if any
                    subset = traffic["TRAFFIC"]
                    for record in subset:
                        if record["PACKET"] != "START":
                            MESSAGEJ.append(record)

                    # append new entry
                    jsonStr = { 'DATE': REPORT_DATE, 'TIME': REPORT_TIME, 'TYPE': REPORT_TYPE[6:], 'PACKET': REPORT_PACKET, 'SYS': REPORT_SYS, 'SRC_ID': REPORT_SRC_ID, 'TS': REPORT_TS, 'TGID': REPORT_TGID, 'ALIAS': REPORT_ALIAS, 'DMRID': REPORT_DMRID, 'CALLSIGN': REPORT_CALLSIGN, 'NAME': REPORT_FNAME, 'DELAY': REPORT_DELAY }
                    MESSAGEJ.append(jsonStr)

                    # keep only the N last
                    MESSAGEJ = MESSAGEJ[-LASTHEARDSIZE:]

                    file.seek(0)
                    json.dump({ "TRAFFIC" : MESSAGEJ }, file, indent=4)
                    file.truncate()

                # add to SQL database
                log_lh_message = '{},{},{},{},{},{},{},TS{},TG{},{},{},{}'.format(_now, REPORT_DELAY, REPORT_TYPE, REPORT_PACKET, REPORT_SYS, REPORT_SRC_ID, alias_call(int(REPORT_SRC_ID), subscriber_ids), REPORT_TS, REPORT_TGID,alias_tgid(int(REPORT_TGID),talkgroup_ids),REPORT_DMRID, alias_short(int(REPORT_DMRID), subscriber_ids))
                logMySQL(log_lh_message)

                # log only to file if system is NOT OpenBridge event (not logging open bridge system, name depends on your OB definitions) 
                # and transmit time is LONGER as N sec (make sense for very short transmits)
                if LASTHEARD_INC and int(float(p[9])) > 0:
                    # append to file
                    with open(LOG_PATH + "lastheard.log", 'a') as lh_logfile:
                        lh_logfile.write(log_lh_message +'\n')

            elif REPORT_PACKET == 'START':
                # add to SQL database
                log_lh_message = '{},{},{},{},{},{},{},TS{},TG{},{},{},{}'.format(_now, 0, REPORT_TYPE, REPORT_PACKET, REPORT_SYS, REPORT_SRC_ID, alias_call(int(REPORT_SRC_ID), subscriber_ids), REPORT_TS, REPORT_TGID,alias_tgid(int(REPORT_TGID),talkgroup_ids),REPORT_DMRID, alias_short(int(REPORT_DMRID), subscriber_ids))
                logMySQL(log_lh_message)

                # open read/write saved history
                with open(LOG_PATH + "lastheard.json", 'r+') as file:
                    traffic = json.load(file)

                    # clear array
                    MESSAGEJ = []

                    # remove all previous START packet if any
                    for record in traffic["TRAFFIC"]:
                        # add padding zeroes if needed
                        if len(record["TIME"]) == 5:
                            record["TIME"] = record["TIME"] + ":00"

                        # add only "END" packets
                        if record["PACKET"] != "START":
                            MESSAGEJ.append(record)

                    # append new entry
                    jsonStr = { 'DATE': REPORT_DATE, 'TIME': REPORT_TIME, 'TYPE': REPORT_TYPE[6:], 'PACKET': REPORT_PACKET, 'SYS': REPORT_SYS, 'SRC_ID': REPORT_SRC_ID, 'TS': REPORT_TS, 'TGID': REPORT_TGID, 'ALIAS': REPORT_ALIAS, 'DMRID': REPORT_DMRID, 'CALLSIGN': REPORT_CALLSIGN, 'NAME': REPORT_FNAME, 'DELAY': 0 }
                    MESSAGEJ.append(jsonStr)

                    # keep only the N last
                    MESSAGEJ = MESSAGEJ[-LASTHEARDSIZE:]

                    file.seek(0)
                    json.dump({ "TRAFFIC" : MESSAGEJ }, file, indent=4)
                    file.truncate()

            elif REPORT_PACKET == 'END WITHOUT MATCHING START':
                jsonStr = { 'DATE': REPORT_DATE, 'TIME': REPORT_TIME, 'TYPE': REPORT_TYPE[6:], 'PACKET': REPORT_PACKET, 'SYS': REPORT_SYS, 'SRC_ID': REPORT_SRC_ID, 'TS': REPORT_TS, 'TGID': REPORT_TGID, 'ALIAS': REPORT_ALIAS, 'DMRID': REPORT_DMRID, 'CALLSIGN': REPORT_CALLSIGN, 'NAME': REPORT_FNAME, 'DELAY': 0 }
            else:
                jsonStr = { 'DATE': _now[0:10], 'TIME': _now[11:16], 'PACKET' : 'UNKNOWN GROUP VOICE LOG MESSAGE' }

            dashboard_server.broadcast( {"TRAFFIC": jsonStr, "CTABLE": CTABLE, 'EMPTY_MASTERS' : EMPTY_MASTERS, "BIGEARS": str(len(dashboard_server.clients))  } )
            
            # logging.info('Process [' + REPORT_PACKET + '] Message Took ' + str(int((ptime.perf_counter() - start) * 1000)) + 'ms')
        else:
            if (len(tgid_allowed) != 0 and REPORT_TGID not in tgid_allowed):
                logging.debug('TG{} NOT ALLOWED'.format(REPORT_TGID))
            logging.debug('{} UNKNOWN LOG MESSAGE'.format(_now[10:19]))
    else:
        logging.debug('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))

    # for key, value in OPCODE.items():
    #     if value == opcode:            
    #         logging.info('Process [' + key + '] Message Took ' + str(int((ptime.perf_counter() - start))) + 'ms')
    #         break

def load_dictionary(_message):
    data = _message[1:]
    logging.debug('Successfully decoded dictionary')
    return loads(data)

######################################################################
#
# COMMUNICATION WITH THE HBlink INSTANCE
#
class report(NetstringReceiver):
    def __init__(self):
        pass

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def stringReceived(self, data):
        process_message(data)

class reportClientFactory(ReconnectingClientFactory):
    def __init__(self):
        logging.info('reportClient object for connecting to HBlink.py created at: %s', self)

    def startedConnecting(self, connector):
        logging.info('Initiating Connection to HBLink Server.')
        if 'dashboard_server' in locals() or 'dashboard_server' in globals():
            dashboard_server.broadcast({ "STATUS": "Connection to HBlink Established" } )

    def buildProtocol(self, addr):
        logging.info('Connected.')
        logging.info('Resetting reconnection delay')
        self.resetDelay()
        return report()

    def clientConnectionLost(self, connector, reason):
        CTABLE['MASTERS'].clear()
        CTABLE['PEERS'].clear()
        CTABLE['OPENBRIDGES'].clear()
        BTABLE['BRIDGES'].clear()
        logging.info('Lost connection.  Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        dashboard_server.broadcast({ "STATUS": "Connection to HBlink Lost" })

    def clientConnectionFailed(self, connector, reason):
        logging.info('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

######################################################################
#
# WEBSOCKET COMMUNICATION WITH THE DASHBOARD CLIENT
#
class dashboard(WebSocketServerProtocol):
    def onConnect(self, request):        
        logging.info('Client connecting: %s', request.peer)
        if 'page' in request.params:
            self.page = request.params["page"][0]
            logging.info('Client Page: %s', self.page)
        else:
            self.page = ""

    def onOpen(self):
        # don't send anything if we are in ccs7manager
        if self.page != "ccs7":
            logging.info('WebSocket connection open.')
            self.factory.register(self)

            _message = {}

            if self.page == "dashboard":
                _message["CTABLE"] = CTABLE
                _message["EMPTY_MASTERS"] = EMPTY_MASTERS

            _message["PACKETS"] = {}
            _message["BIGEARS"] = str(len(dashboard_server.clients))
            _message["LISTENERS"] = LISTENERSJ
            _message["CONTACTS"] = CONTACTSJ

            INITIALLIST = []

            if SQL_LOG == True:
                _message["USERS"] = createlocalUsersFromSql()
            else:
                with open(PATH + LOCAL_SUB_FILE, 'r') as infile:
                    _message["USERS"] = json.load(infile)

            # read saved history or create traffic file for later
            if os.path.exists(LOG_PATH + "lastheard.json"):
                if SQL_LOG == True:                
                    INITIALLIST = createlogLastFromSql(False)
                else:
                    with open(LOG_PATH + "lastheard.json", 'r') as infile:
                        _traffic = json.load(infile)

                        if _traffic and _traffic["TRAFFIC"]:
                            INITIALLIST = reversed(_traffic["TRAFFIC"]) 
                            # _traffic = reversed(_traffic["TRAFFIC"])
                            # _tglist = list(TGID_ORDER.split(","))
                            # for record in _traffic:
                            #     if record["TGID"] in _tglist:
                            #         INITIALLIST.append(record)
                        else:
                            logging.info("Creating empty " + LOG_PATH + "lastheard.json")
                            with open(LOG_PATH + "lastheard.json", 'w') as outfile:
                                json.dump({ "TRAFFIC" : [] }, outfile)
            else:
                logging.info("Creating empty " + LOG_PATH + "lastheard.json")
                with open(LOG_PATH + "lastheard.json", 'w') as outfile:
                    json.dump({ "TRAFFIC" : [] }, outfile)

            # sorted in reverse order last in log becomes first to display
            # https://linuxhint.com/sort-json-objects-python/
            _message["PACKETS"] = { "TRAFFIC": sorted(INITIALLIST, key=lambda k: (k["DATE"]+" "+k["TIME"]), reverse=True)[:TRAFFICSIZE] }

            self.sendMessage(json.dumps({ "CONFIG": _message }, ensure_ascii = False).encode('utf-8'))

            # if caller pages is bridges, send bridges
            if self.page == "bridges":
                self.sendMessage(json.dumps({ "BTABLE": BTABLE }, ensure_ascii = False).encode('utf-8'))

            mapIpAdresses()

            logger.info('Deleting INITIALLIST after init')
            del _message
            del INITIALLIST

    def onMessage(self, payload, isBinary):
        try: 
            if not isBinary:
                _command = json.loads(payload.decode('utf-8'))
                logging.info("command received: {}".format(_command))
                if _command:
                    if _command.get("request"):
                        if _command["request"] == "loglast":
                            # depending on SQL_LOG use SQL or text file option
                            self.sendMessage(json.dumps({"LOGLAST": createlogLastFromSql(True) if SQL_LOG == True else createLogTableJson()  }, ensure_ascii = False).encode('utf-8'), isBinary)
                        elif _command["request"] == "user" and _command["callsign"]:
                            response = ""

                            with open(PATH + SUBSCRIBER_FILE, 'r') as infile:
                                USERS = json.load(infile)["users"]
                                for user in USERS:
                                    if user["callsign"] == _command["callsign"]:
                                        response = json.dumps({"USER": user }, ensure_ascii = False).encode('utf-8')
                                        self.sendMessage(response, isBinary)
                                        break

                                logging.info("response sent: {}".format(response))
                        elif _command["request"] == "userslist":
                            self.sendMessage(json.dumps({"USERS": createlocalUsersFromSql() }, ensure_ascii = False).encode('utf-8'), isBinary)
                    elif _command.get("fileurl") and _command["fileurl"].startswith("http"):
                        filename = fetchRemoteUsersFiles(_command["fileurl"])
                        self.sendMessage(json.dumps({"FILENAME": filename }, ensure_ascii = False).encode('utf-8'), isBinary)
                        # with open(filename, 'r') as infile:                            
                        #     self.sendMessage(json.dumps(json.load(infile), ensure_ascii = False).encode('UTF-8'))
                        #     infile.close()
            
        except CalledProcessError as err:
            logging.info('Error: %s', err)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)
        
    def onClose(self, wasClean, code, reason):
        logging.info('WebSocket connection closed: %s', reason)

class dashboardFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = {}

    def register(self, client):
        if client not in self.clients:
            logging.info('registered client %s', client.peer)
            self.clients[client] = time()

    def unregister(self, client):
        if client in self.clients:
            logging.info('unregistered client %s', client.peer)
            del self.clients[client]

    def broadcast(self, msg):
        logging.debug('broadcasting message to: %s', self.clients)
        for c in self.clients:
            c.sendMessage(json.dumps(msg, ensure_ascii = False).encode('UTF-8'))
            logging.debug('message sent to %s', c.peer)
    

######################################################################
#
# STATIC WEBSERVER
#
class staticHtmlFile(Resource):
    def __init__(self, file_Name, file_Folder, file_contentType):
        self.file_Name = file_Name
        self.file_Folder = file_Folder
        self.file_contentType = file_contentType
        Resource.__init__(self)

    def render_GET(self, request):
        filepath = "{}/{}".format(PATH + self.file_Folder, self.file_Name.decode("UTF-8"))

        if os.path.exists(filepath):
            request.setHeader('content-disposition', 'filename=' + self.file_Name.decode("UTF-8"))
            request.setHeader('content-type', self.file_contentType)
            return replaceSystemStrings(get_template(filepath)).encode("utf-8")

        request.setResponseCode(http.NOT_FOUND)
        request.finish()
        return NoResource()

class staticFile(Resource):
    def __init__(self, file_Name, file_Folder, file_contentType):
        self.file_Name = file_Name
        self.file_Folder = file_Folder
        self.file_contentType = file_contentType        
        Resource.__init__(self)

    def render_GET(self, request):
        @defer.inlineCallbacks
        def _feedfile():
            if self.file_Folder != "/tmp":
                filepath = "{}/{}".format(PATH + self.file_Folder, self.file_Name.decode("UTF-8"))
            else:
                filepath = "{}/{}".format(self.file_Folder, self.file_Name.decode("UTF-8"))

            self.file_size = os.path.getsize(filepath)

            logging.info(filepath)

            @defer.inlineCallbacks
            def _setContentDispositionAndSend(file_path, file_name, content_type):
                request.setHeader('content-disposition', 'filename=' + file_name.decode("UTF-8"))
                request.setHeader('content-length', str(self.file_size))
                request.setHeader('content-type', content_type)

                with open(file_path, 'rb') as f:                    
                    yield FileSender().beginFileTransfer(f, request)
                    f.close()

                defer.returnValue(0)

            if os.path.exists(filepath):
                yield _setContentDispositionAndSend(filepath, self.file_Name, self.file_contentType)
            else:
                request.setResponseCode(http.NOT_FOUND)
            
            request.finish()

            defer.returnValue(0)

        _feedfile()
        return server.NOT_DONE_YET

class loglast(Resource):
    def __init__(self):
        Resource.__init__(self)

    def render_GET(self, request):
        return str.encode(replaceSystemStrings(get_template(PATH + "templates/loglast_template.html")))

class ccs7manager(Resource):
    def __init__(self):
        Resource.__init__(self)

    def render_GET(self, request):
        return str.encode(replaceSystemStrings(get_template(PATH + "templates/ccs7manager.html")))

class IAuthenticated(Interface):
    mode = Attribute("A value 0 or 1 meaning User or Admin")
    value = Attribute("A boolean indicating session has been authenticated")

@implementer(IAuthenticated)
class Authenticated(object):
    def __init__(self, session):
        self.value = False
        self.mode = 0

registerAdapter(Authenticated, Session, IAuthenticated)

def index_template():
    return replaceSystemStrings(get_template(PATH + "templates/index_template.html")).encode('utf-8')

class web_server(Resource):
    def __init__(self):
        Resource.__init__(self)

    def getChild(self, name, request):
        session = request.getSession()
        authenticated = IAuthenticated(session)
        if authenticated.value != True:
            return self

        page = name.decode("utf-8")

        if page == '' or page == 'index.html':
            return self

        if page == 'loglast.html':
            return loglast()

        if page == 'ccs7manager.html':
            return ccs7manager()

        # deal with static files (images, css etc...)
        # call static file with file name, location folder, controlType
        #
        if page.endswith(".html") or page.endswith(".htm"):
            return staticHtmlFile(name, "html", "text/html; charset=utf-8")
        if page.endswith(".css"):
            return staticFile(name, "css", "text/css; charset=utf-8")
        elif page.endswith(".js"):
            return staticFile(name, "scripts", "application/javascript; charset=utf-8")
        elif page.endswith(".jpg") or page.endswith(".jpeg"):
            return staticFile(name, "images", "image/jpeg")
        elif page.endswith(".gif"):
            return staticFile(name, "images", "image/gif")
        elif page.endswith(".png"):
            return staticFile(name, "images", "image/png")
        elif page.endswith(".svg"):
            return staticFile(name, "images", "image/svg+xml")
        elif page.endswith(".ico"):
            return staticFile(name, "images", "image/x-icon")            
        elif page.endswith(".json"):            
            return staticFile(name, "assets", "application/json")
        elif page.endswith(".txt"):
            return staticFile(name, "html", "text/plain")
        elif page.endswith(".woff2"):
            return staticFile(name, "webfonts", "font/woff2;")
        elif page.endswith(".woff"):
            return staticFile(name, "webfonts", "font/woff;")
        elif page.endswith(".ttf"):
            return staticFile(name, "webfonts", "font/ttf;")
        elif page.endswith(".xls") or page.endswith(".xlsx"):
            # if file is in list generated from sql table
            if page in ["table1", "table2", "table3"]:
                tableToExcel(page[:page.index(":")])
                return staticFile(name, "/tmp", "application/vnd.ms-excel")
            else:
                return staticFile(name, "html", "application/vnd.ms-excel")

        return NoResource()

    def render_GET(self, request):
        global MOBILEPHONE

        admin_auth = False
        logging.info('static website requested: %s', request)
        session = request.getSession()
        authenticated = IAuthenticated(session)
        userAgent = auth = request.getHeader('User-Agent')

        try:
            if userAgent.lower().index("mobile"):
                MOBILEPHONE = True
            else:
                MOBILEPHONE = False
        except:
            MOBILEPHONE = False

        url = URL.fromText(request.uri.decode('ascii'))
        if len(url.get("admin")) > 0:
            admin_auth = True

        if WEB_AUTH or admin_auth:
            admin_login = ADMIN_USER.encode('utf-8')
            admin_password = ADMIN_PASS.encode('utf-8')

            user = WEB_USER.encode('utf-8')
            password = WEB_PASS.encode('utf-8')

            auth = request.getHeader('Authorization')
            if auth and auth.split(' ')[0] == 'Basic':
                decodeddata = base64.b64decode(auth.split(' ')[1])
                if (decodeddata.split(b':') == [user, password] and not admin_auth) or (decodeddata.split(b':') == [admin_login, admin_password] and admin_auth):
                    global BUTTONBAR_HTML

                    logging.info('Authorization OK')
                    authenticated.value = True
                    if decodeddata.split(b':') == [user, password]:
                        authenticated.mode = 0
                        # update button bar template
                        logging.info('user logging, switching to user menu')
                        BUTTONBAR_HTML = get_template(PATH + "templates/buttonbar.html")
                    else:
                        authenticated.mode = 1
                        # update button bar template
                        logging.info('admin logging, switching to admin menu')
                        BUTTONBAR_HTML = get_template(PATH + "templates/admin_buttonbar.html")

                    return index_template()

            authenticated.value = False
            authenticated.mode = 0
            request.setResponseCode(http.UNAUTHORIZED)
            request.setHeader('www-authenticate', 'Basic realm="realmname"')
            logging.info('Someone wanted to get access without authorization')

            return "<html<head></hread><body style=\"background-color: #EEEEEE;\"><br><br><br><center> \
                    <fieldset style=\"width:600px;background-color:#e0e0e0e0;text-algin: center; margin-left:15px;margin-right:15px; \
                     font-size:14px;border-top-left-radius: 10px; border-top-right-radius: 10px; \
                     border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;\"> \
                  <p><font size=5><b>Authorization Required</font></p></filed></center></body></html>".encode('utf-8')
        else:
            authenticated.value = True
            authenticated.mode = 0
            return index_template()

# Function to accept offers from the client ..
def accept(offers):
    for offer in offers:
        if isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename = (LOG_PATH + LOG_NAME),
        filemode='a',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logger = logging.getLogger(__name__)

    logging.info('monitor.py starting up')

    logger.info('\n\n\tCopyright (c) 2016, 2017, 2018, 2019\n\tThe Regents of the K0USY Group. All rights reserved.' \
                '\n\n\tPython 3 port:\n\t2019 Steve Miller, KC1AWV <smiller@kc1awv.net>' \
                '\n\n\tHBMonitor v1 SP2ONG 2019-2021' \
                '\n\n\tHBJSON v3.1.0:\n\t2021, 2022 Jean-Michel Cohen, F4JDN <f4jdn@outlook.fr>\n\n')

    # Check lastheard.log file
    if os.path.isfile(LOG_PATH+"lastheard.log"):
      try:
         check_call("sed -i -e 's|\\x0||g' {}".format(LOG_PATH+"lastheard.log"), shell=True)
         logging.info('Check lastheard.log file')
      except CalledProcessError as err:
         print(err)
    
    # Create Static Website index file
    sitelogo_html = get_template(PATH + "templates/sitelogo.html")
    BUTTONBAR_HTML = get_template(PATH + "templates/buttonbar.html")

    # get tgid filter
    tgid_allowed = get_tgidf()

    try:
        # Download alias files
        result = try_download(PATH, PEER_FILE, PEER_URL, (FILE_RELOAD * 86400))
        logging.info(result)
    except:
        pass

    try:
        result = try_download(PATH, SUBSCRIBER_FILE, SUBSCRIBER_URL, (FILE_RELOAD * 86400))
        logging.info(result)
    except:
        pass

    try:
        result = try_download(PATH, LOCAL_SUB_FILE, LOCAL_SUBSCRIBER_URL, (FILE_RELOAD * 3600))
        logging.info(result)
    except:
        pass
    
    # Make Alias Dictionaries
    peer_ids = mk_full_id_dict(PATH, PEER_FILE, 'peer')
    if peer_ids:
        logging.info('ID ALIAS MAPPER: peer_ids dictionary is available')

    subscriber_ids = mk_full_id_dict(PATH, SUBSCRIBER_FILE, 'subscriber')
    if subscriber_ids:
        logging.info('ID ALIAS MAPPER: subscriber_ids dictionary is available')
        
    local_subscriber_ids = mk_full_id_dict(PATH, LOCAL_SUB_FILE, 'local_subscriber')
    if subscriber_ids:
        logging.info('ID ALIAS MAPPER: local_subscriber_ids dictionary is available')

    talkgroup_ids = mk_full_id_dict(PATH, TGID_FILE, 'tgid')
    if talkgroup_ids:
        logging.info('ID ALIAS MAPPER: talkgroup_ids dictionary is available')

    local_subscriber_ids = mk_full_id_dict(PATH, LOCAL_SUB_FILE, 'subscriber')
    if local_subscriber_ids:
        logging.info('ID ALIAS MAPPER: local_subscriber_ids added to subscriber_ids dictionary')
        subscriber_ids.update(local_subscriber_ids)

    local_talkgroup_ids = mk_full_id_dict(PATH, LOCAL_TGID_FILE, 'tgid')
    if local_talkgroup_ids:
        logging.info('ID ALIAS MAPPER: local_talkgroup_ids added to talkgroup_ids dictionary')
        talkgroup_ids.update(local_talkgroup_ids)

    local_peer_ids = mk_full_id_dict(PATH, LOCAL_PEER_FILE, 'peer')
    if local_peer_ids:
        logging.info('ID ALIAS MAPPER: local_peer_ids added peer_ids dictionary')
        peer_ids.update(local_peer_ids)

    if os.path.isfile(LOG_PATH + "contacts_fr_dept.json"):
        with open(LOG_PATH + "contacts_fr_dept.json", 'r') as file:
            CONTACTSJ = json.load(file)

    # Start update loop
    update_stats = task.LoopingCall(build_stats)
    update_stats.start(FREQUENCY)

    # Start a timeout loop
    if CLIENT_TIMEOUT > 0:
        timeout = task.LoopingCall(timeout_clients)
        timeout.start(10)

    # Connect to HBlink
    reactor.connectTCP(HBLINK_IP, HBLINK_PORT, reportClientFactory())

    # Create websocket server to push content to clients
    dashboard_server = dashboardFactory('ws://*:{}'.format(SOCKET_SERVER_PORT))
    dashboard_server.protocol = dashboard

    dashboard_server.setProtocolOptions(perMessageCompressionAccept=accept)

    reactor.listenTCP(SOCKET_SERVER_PORT, dashboard_server)

    # Create static web server to push initial index.html
    root = web_server()
    factory = Site(root)
    endpoint = endpoints.TCP4ServerEndpoint(reactor, JSON_SERVER_PORT)
    endpoint.listen(factory)

    # reactor.listenTCP(JSON_SERVER_PORT, factory)

    # create ipmap if needed
    initIpMap()

    reactor.run()

