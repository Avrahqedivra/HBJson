import sys

from config import *
from crc16 import *

if __name__ == '__main__':  
  if len(sys.argv[1:]) == 0:
    print("a callsign parameter is expected")
  else:
    callsign = sys.argv[1:][0].upper()
    code = str(crc16(callsign, WEB_SECRETKEY))
    print("\r\nLogin/Passcode generator for HBJSON v3.3.0:\r\nCopyright (c)  2023 Jean-Michel Cohen, F4JDN <f4jdn@outlook.fr>\\r\n")
    print(callsign + " passcode is " + code + "\n\n")
