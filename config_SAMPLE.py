REPORT_NAME     = "Name of the monitored HBlink" # Name of the monitored HBlink system
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

# Put list of NETWORK_ID from OPB links to don't show local traffic in lastheard, for example: "260210,260211,260212"
OPB_FILTER = ""
# tg1, tg2 etc to be excluded, for example "800,801,802,3339"
TGID_FILTER = ""
# tg order on html monitor page, for example "38,7,39,777"
TGID_ORDER = ""
# all tgid not in this list will be excluded. if empty all will be allowed
TGID_MANAGE = ""
# TG to hilite
TGID_HILITE = ""
# TG colors is a json array string of tgid and hex rgb
TGID_COLORS = '{ "tx":"#fbd379", "ind":"#fefefe", "38":"#569cd6", "7":"#fca33c", "39":"#a3e978", "777":"#bc7ebb" }'
# dynamic tg, if not filtred by TGID_FILTER, tg will be added dynamicaly to dashboard beside those in TG_ORDER
DYNAMIC_TG = False
# hide OMs with DMRID starting with, for example with "208,206"
HIDE_DMRID = ""
# beacons/icons pairs, for example '{ "2080000":"unlicenced.png", "2060000":"unlicenced.png" }'
TGID_BEACONS = '{ "2080000":"unlicenced.png" }'

# Authorization of access to dashboard as admin
# use http://mysite:port?admin to log as admin
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'

# Authorization of access to dashboard# as user
WEB_AUTH =  False
WEB_USER =  'hblink'
WEB_PASS =  'hblink'

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

# Files and stuff for loading alias files for mapping numbers to names
PATH            = './'                           # MUST END IN '/'
PEER_FILE       = 'peer_ids.json'                # Will auto-download from DMR-MARC
SUBSCRIBER_FILE = 'subscriber_ids.json'          # Will auto-download from DMR-MARC
TGID_FILE       = 'talkgroup_ids.json'           # User provided, should be in "integer TGID, TGID name" format
LOCAL_SUB_FILE  = 'local_subscriber_ids.json'    # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
LOCAL_PEER_FILE = 'local_peer_ids.json'          # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
FILE_RELOAD     = 1                              # Number of days before we reload DMR-MARC database files
PEER_URL        = 'https://database.radioid.net/static/rptrs.json'
SUBSCRIBER_URL  = 'https://database.radioid.net/static/users.json'
LOCAL_SUBSCRIBER_URL  = 'local_subscriber_ids.json'     # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC

# Settings for log files
LOG_PATH        = './log/'                       # MUST END IN '/'
LOG_NAME        = 'hbmon.log'
