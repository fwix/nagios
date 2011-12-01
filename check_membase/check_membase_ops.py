#!/usr/bin/env python

import simplejson
import urllib2
import sys
import optparse

def GetMembasePoolOps(host, pool, user, password, port=8091):
  url = 'http://%s:%s/pools/%s/buckets' % (host, port, pool)

  auth_handler = urllib2.HTTPBasicAuthHandler()
  auth_handler.add_password(None, url, user, password)

  opener = urllib2.build_opener(auth_handler)
  urllib2.install_opener(opener)
  stats = urllib2.urlopen(url)
  stats = stats.read()
  stats = simplejson.loads(stats)
  stats = stats[0]

  return stats

def CheckMembasePoolOps(stats):
  res = 'OK'
  status = 0
  opsPerSec = stats['basicStats']['opsPerSec']
  quotaPercentUsed = stats['basicStats']['quotaPercentUsed']
  itemCount = stats['basicStats']['itemCount']
  diskUsed = stats['basicStats']['diskUsed']
  memUsed = stats['basicStats']['memUsed']
  diskFetches = stats['basicStats']['diskFetches']

  result = '%s: %s ops/sec, %s items|opsPerSec=%s quotaPercentUsed=%s itemCount=%s diskUsed=%s memUsed=%s diskFetches=%s' % \
        (res, opsPerSec, itemCount, opsPerSec, quotaPercentUsed, 
         itemCount, diskUsed, memUsed, diskFetches)

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

  stats = GetMembasePoolOps(hostname, pool, user, passwd)
  status, result = CheckMembasePoolOps(stats)
  print result
  sys.exit(status)
