#!/usr/bin/env python

import simplejson
import urllib2
import sys
import optparse

def GetMembasePoolStats(host, pool, user, password, port=8091):
  url = 'http://%s:%s/pools/%s' % (host, port, pool)

  auth_handler = urllib2.HTTPBasicAuthHandler()
  auth_handler.add_password(None, url, user, password)

  opener = urllib2.build_opener(auth_handler)
  urllib2.install_opener(opener)
  stats = urllib2.urlopen(url)
  stats = stats.read()
  stats = simplejson.loads(stats)

  return stats

def CheckMembasePoolStats(stats):
  res = 'OK: all nodes are healthy'
  status = 0
  ram_quota_used = stats['storageTotals']['ram']['quotaUsed']
  ram_quota_total = stats['storageTotals']['ram']['quotaTotal']
  hdd_used = stats['storageTotals']['hdd']['used']

  nodes = stats['nodes']
  for node in nodes:
    if node['status'] != 'healthy':
      res = 'WARNING: there are unhealthy nodes'

  result = '%s|ram_quota_used=%s ram_quota_total=%s hdd_used=%s' % \
           (res, ram_quota_used, ram_quota_total, hdd_used)

  return status, result

def ParseCommandLine():
  parser = optparse.OptionParser()
  parser.add_option('-H', help='hostname', dest='hostname', action='store')
  parser.add_option('-u', help='username', dest='username', action='store', default='none')
  parser.add_option('-p', help='password', dest='password', action='store', default='none')
  parser.add_option('--pool', help='membase pool', dest='pool', action='store', default='default')
  return parser


if __name__ == '__main__':
  parser = ParseCommandLine()
  options, args = parser.parse_args()

  hostname = options.hostname
  pool = options.pool
  user = options.username
  passwd = options.password

  stats = GetMembasePoolStats(hostname, pool, user, passwd)
  status, result = CheckMembasePoolStats(stats)
  print result
  sys.exit(status)
