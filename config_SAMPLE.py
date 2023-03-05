REPORT_NAME     = "HBJSON Monitor for HBLINK"   # Name of the monitored HBlink system
#
CONFIG_INC      = True                          # Include HBlink stats
HOMEBREW_INC    = True                          # Display Homebrew Peers status
LASTHEARD_INC   = True                          # Display lastheard table on main page
BRIDGES_INC     = True                          # Display Bridge status and button
EMPTY_MASTERS   = False                         # Display (True) or not (False) empty master in status

HBLINK_IP       = '127.0.0.1'                   # HBlink's IP Address
HBLINK_PORT     = 4321                          # HBlink's TCP reporting socket
FREQUENCY       = 10                            # Frequency to push updates to web clients
SOCKET_SERVER_PORT = 9020                       # Websocket server for realtime monitoring
JSON_SERVER_PORT = 9990                         # Has to be above 1024 if you're not running as root
DISPLAY_LINES =  20                             # number of lines displayed in index_template
CLIENT_TIMEOUT  = 0                             # Clients are timed out after this many seconds, 0 to disable

# list of NETWORK_ID from OPB links not to show in local "lastheard" traffic, for example: "260210,260211,260212"
OPB_FILTER = ""
# allowed Backend OBP, if specified, precise all allowed SRC_ID, for example { "OBP-GLOBAL": { "20881", "20883" } }
OPB_BACKEND = { "": { "" } }
# ids of tg to be excluded, for example "800,801,802,3339"
TGID_FILTER = ""
# ids of tg order on html monitor page, for example "38,7,39,777"
TGID_ORDER = ""
# tg optional settings, for example "tgid": { "title-before": "title", "hide-dmrid": "208, 206" }
# "*" are the default settings, you can override default by specifying a setting in tg
# IMPORTANT keep the "*" line at the END. "title-before" present will name tg from ALIAS field 
TGID_SETTINGS = '{  "33": { "title-before": "F4KNH Radio-Club", "show-columns": "+++++++---", "title-style": "color: orange;", "header-before": "Licensed HAM" }, \
                    "38": { "title-before": "SHIELD", "hide-dmrid": "208, 206", "header-before": "VOIP and Unlicensed" }, \
                    "39": { "title-before": "SHIELD Test", "hide-dmrid": "208, 206" }, \
                    "75": { "title-before": "DMR75 National", "hide-dmrid": "208, 206" }, \
                     "*": { "title-before": "auto", "show-empty": false, "show-columns": "++++++++++", "title-style": "color: gold;", "header-before": "auto", "header-style": "color: white;" } \
                }'

# all tgid not in this list will be excluded. if empty all will be allowed
TGID_ALLOWED = ""
# TG to hilite
TGID_HILITE = ""
# TG colors is a json array string of tgid and hex rgb
TGID_COLORS = '{ "tx":"#fbd379", "ind":"#fefefe", "38":"#569cd6", "7":"#fca33c", "39":"#a3e978", "777":"#bc7ebb" }'
# dynamic tg, if not filtred by TGID_FILTER, tg will be added dynamicaly to dashboard beside those in TG_ORDER
DYNAMIC_TG = False
# hide OMs with DMRID starting with, for example with "208,206" (superseded by TGID_SETTINGS)
HIDE_DMRID = "#"
# beacons/icons pairs, for example '{ "2080000":"shield.png", "2060000":"shield.png" }'
TGID_BEACONS = '{ "2000008":"shield.png" }'

# ip, sites and services to be monitored (see also status button in menubar template)
TO_BE_MONITORED = [
    {"name": "HB1", "type": "tcp", "ip": "localhost", "port": 1234, "action": "connect"},
    {"name": "HB2", "type": "tcp", "ip": "127.0.0.1", "port": 4567, "action": "connect"},
    {"name": "IDF", "type": "tcp", "ip": "orange.fr", "action": "ping"},
    {"name": "SITE", "type": "tcp", "ip": "monsite.url", "action": "ping"},
    {"name": "TP1", "service": "analog_bridged1"},
    {"name": "TP2", "service": "analog_bridged2"}
]

# sets default theme (dark or light)
THEME = "theme-dark"

# Authorization of access to dashboard as admin
# use http://mysite:port?admin to log as admin
ADMIN_USER = 'admin'

# Authorization of access to dashboard# as user
WEB_AUTH =  False

# secret salt key for passcode generator
WEB_SECRETKEY = "SECRETKEY"

# Authorization of access to SQL
SQL_LOG       = False
SQL_USER      = 'SQLUSER'
SQL_PASS      = 'SQLPASSWORD'
SQL_HOST      = 'localhost'
SQL_DATABASE  = 'hbjson'

# Dispay lastactive TG table
LAST_ACTIVE_TG  = False
# Max lines in lastactive table (0 means all TGs defined in TG_ORDER list)
LAST_ACTIVE_SIZE = 0

# Lastheard file size
LAST_HEARD_SIZE = 2000
# Nb lines in first packet sent to dashboard
TRAFFIC_SIZE    = 500
# Display percent
DISPLAY_PERCENT = True

# Files and stuff for loading alias files for mapping numbers to names
PATH            = './'                           # MUST END IN '/'
PEER_FILE       = 'peer_ids.json'                # Will auto-download from DMR-MARC
SUBSCRIBER_FILE = 'subscriber_ids.json'          # Will auto-download from DMR-MARC
TGID_FILE       = 'talkgroup_ids.json'           # User provided, should be in "integer TGID, TGID name" format
LOCAL_SUB_FILE  = 'local_subscriber_ids.json'    # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
LOCAL_PEER_FILE = 'local_peer_ids.json'          # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
LOCAL_TGID_FILE = 'local_talkgroup_ids.json'     # User provided (optional, leave '' if you don't use it)
FILE_RELOAD     = 1                              # Number of days before we reload DMR-MARC database files
PEER_URL        = 'https://database.radioid.net/static/rptrs.json'
SUBSCRIBER_URL  = 'https://database.radioid.net/static/users.json'
LOCAL_SUBSCRIBER_URL  = 'local_subscriber_ids.json'     # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC

# Settings for log files
LOG_PATH        = './log/'                       # MUST END IN '/'
LOG_NAME        = 'hbmon.log'
