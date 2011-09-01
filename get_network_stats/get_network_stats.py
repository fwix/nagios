#!/usr/bin/env python
#
# This script is intended for use on a linux system
# It's only been tested on Centos 5, so YMMV
#
# The GetInterfaces function was mostly borrowed from:
# http://neverfear.org/blog/view/132/Fetching_network_statistics_Python_and_Linux
#
# 8/25/2011 Vikram Adukia <adukia@fwix.com>
# - initial release

import re
import optparse
import sys
import time
 
def GetInterfaces():
  ret = {}
  f = open("/proc/net/dev", "r");
  data = f.read()
  f.close()
 
  r = re.compile("[:\s]+")
 
  lines = re.split("[\r\n]+", data)
  for line in lines[2:]:
    columns = r.split(line)
    if len(columns) < 18:
      continue
    info                  = {}
    info["rx_bytes"]      = int(columns[2])
    info["rx_packets"]    = int(columns[3])
    info["rx_errors"]     = int(columns[4])
    info["rx_dropped"]    = int(columns[5])
    info["rx_fifo"]       = int(columns[6])
    info["rx_frame"]      = int(columns[7])
    info["rx_compressed"] = int(columns[8])
    info["rx_multicast"]  = int(columns[9])
 
    info["tx_bytes"]      = int(columns[10])
    info["tx_packets"]    = int(columns[11])
    info["tx_errors"]     = int(columns[12])
    info["tx_dropped"]    = int(columns[13])
    info["tx_fifo"]       = int(columns[14])
    info["tx_frame"]      = int(columns[15])
    info["tx_compressed"] = int(columns[16])
    info["tx_multicast"]  = int(columns[17])
 
    iface                 = columns[1]
    ret[iface] = info
  return ret

def ParseCommandLine():
  desc = """Intended to pair with pnp4nagios in order to
provide stats for your network usage. This script will *always*
return as an OK for nagios.
Example Usage: %s -i eth0,eth1""" % sys.argv[0]
  parser = optparse.OptionParser(description=desc)
  parser.add_option('-i', 
                    help='comma seperated list of interfaces', 
                    dest='interfaces', 
                    action='store', 
                    default='eth0')
  return parser

if __name__ == '__main__':
  parser = ParseCommandLine()
  options, args = parser.parse_args()
  interfaces = options.interfaces
  interface_list = interfaces.split(',')

  # we want to get the transfer rate over 1 second,
  # so get a starting and ending point
  interface_info_start = GetInterfaces()
  time.sleep(1)
  interface_info_end = GetInterfaces()

  # just fill in some blank data to start with
  res = 'OK:'
  perf = ''

  for i in interface_list:
    # just in case an interface is put on the command line
    # but doesn't exist, check for it.
    if i not in interface_info_start.keys():
      continue

    # grab our start and end data points
    rx_start = interface_info_start[i]['rx_bytes']
    tx_start = interface_info_start[i]['tx_bytes']
    rx_end = interface_info_end[i]['rx_bytes']
    tx_end = interface_info_end[i]['tx_bytes']

    # we have our start and ends, now grab the difference
    rx = rx_end - rx_start
    tx = tx_end - tx_start
    res = '%s %s_rx_bytes: %s %s_tx_bytes: %s' % (res, i, rx, i, tx)
    perf = '%s %s_rx_bytes=%s %s_tx_bytes=%s' % (perf, i, rx, i, tx)

  result = '%s|%s' % (res, perf)
  print result
