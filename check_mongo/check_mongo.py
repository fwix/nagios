#!/usr/bin/env python
#
# This script requires pymongo to be installed
# It's only been tested on Centos 5, so YMMV
#
# 8/29/2011 Vikram Adukia <adukia@fwix.com>
# - initial release

import pprint
import pymongo
import optparse
import sys
import time

class NagiosMongo:
  def __init__(self, hostlist, replicaset=None, DEBUG=False):
    self.DEBUG = DEBUG
    self.conn = pymongo.Connection(hostlist)
    self.db = pymongo.database.Database(self.conn, 'admin')

  def isMaster(self):
    res = self.db.command('isMaster')
    if self.DEBUG: 
      pprint.pprint(res)

    ismaster = res['ismaster']
    return ismaster

  def serverStatus(self):
    stats = self.db.command('serverStatus')
    if self.DEBUG: pprint.pprint(stats)
    return stats

  def get_network_io(self):
    stats_start = self.serverStatus()['network']
    time.sleep(1)
    stats_end = self.serverStatus()['network']
    res = 'OK:'
    perf = ''
    for i in stats_start.keys():
      start = stats_start[i]
      end = stats_end[i]
      rate = end - start
      opname = '%s_net' % i
      res = '%s %s:%s/s' % (res, opname, rate)
      perf = '%s %s=%s' % (perf, opname, rate)

    result = '%s|%s' % (res, perf)
    return 0, result

  def get_memory_info(self):
    stats = self.serverStatus()['mem']
    res = 'OK:'
    perf = ''
    for i in stats.keys():
      if i == 'bits' or i == 'supported':
        continue
      memname = '%s_mem' % i
      res = '%s %s:%sMB' % (res, memname, stats[i])
      perf = '%s %s=%s' % (perf, memname, stats[i])

    result = '%s|%s' % (res, perf)
    return 0, result

  def get_opcounter_rate(self):
    stats_start = self.serverStatus()['opcounters']
    time.sleep(1)
    stats_end = self.serverStatus()['opcounters']
    res = 'OK:'
    perf = ''
    for i in stats_start.keys():
      start = stats_start[i]
      end = stats_end[i]
      rate = end - start
      opname = '%s_op' % i
      res = '%s %s:%s/s' % (res, opname, rate)
      perf = '%s %s=%s' % (perf, opname, rate)

    result = '%s|%s' % (res, perf)
    return 0, result

  def get_connection_count(self):
    stats = self.serverStatus()['connections']
    current = stats['current']
    total = stats['available']
    percent = (float(current) / float(total)) * 100

    if percent >= 95:
      status = 2
      res = 'CRITICAL'
    elif percent >= 60:
      status = 1
      res = 'WARNING'
    else:
      status = 0
      res = 'OK'

    result = '%s: %s%% connections used (%s out of %s)|connections=%s' % \
             (res, percent, current, total, current)
    return status, result

  def check_replication(self):
    if self.isMaster():
      status = 0
      result = 'OK: nothing to check, this is the master|lag=0'
      return status, result

    host = self.serverStatus()['host'].split('.')[0]

    replica_members = self.db.command('replSetGetStatus')['members']
    if self.DEBUG: pprint.pprint(replica_members)
    primary_optime = 0
    my_optime = -1
    my_state = 'RECOVERING'

    for i in replica_members:
      name = i['name'].split(':')[0]
      stateStr = i['stateStr']
      if stateStr == 'PRIMARY':
        primary_optime = i['optime'].time
        continue
      elif name != host:
        continue

      my_optime = i['optime'].time
      my_state = stateStr

    lag = primary_optime - my_optime

    if my_state != 'SECONDARY':
      status = 2
      result = 'CRITICAL: host is in %s state' % my_state
    elif lag >= 7200:
      status = 2
      result = 'CRITICAL: %s is %ss behind|lag=%s' % (my_state, lag, lag)
    elif lag >= 3600:
      status = 1
      result = 'WARNING: %s is %ss behind|lag=%s' % (my_state, lag, lag)
    else:
      status = 0
      result = 'OK: %s is %ss behind|lag=%s' % (my_state, lag, lag)

    return status, result

def ParseCommandLine():
  parser = optparse.OptionParser()
  parser.add_option('-m', 
                    help='mode is one of: '
                         'opcounters, connections, network_io, replication'
                         'memory',
                    dest='mode', 
                    action='store', 
                    default='opcounters')
  parser.add_option('-H', '--hostname', help='hostname', action='store')
  parser.add_option('-p', 
                    '--port', 
                    help='port', 
                    action='store', 
                    type='int', 
                    default=27017)
  return parser
    
if __name__ == '__main__':
  parser = ParseCommandLine()
  options, args = parser.parse_args()
  hostname = options.hostname
  port = options.port
  mode = options.mode

  host = '%s:%s' % (hostname, port)
  try:
    a = NagiosMongo(host)
  except:
    status = 2
    result = 'CRITICAL: unable to connect to mongodb on %s' % host
    print result
    sys.exit(status)
  if mode == 'opcounters':
    status, result = a.get_opcounter_rate()
  elif mode == 'connections':
    status, result = a.get_connection_count()
  elif mode == 'network_io':
    status, result = a.get_network_io()
  elif mode == 'replication':
    status, result = a.check_replication()
  elif mode == 'memory':
    status, result = a.get_memory_info()

  print result
  sys.exit(status)
