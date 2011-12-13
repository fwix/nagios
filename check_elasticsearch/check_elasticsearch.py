#!/usr/bin/env python

import pyes
import pprint
import socket
import optparse
import sys

class ElasticConnect:
  def __init__(self, hostname, port):
    self.conn = pyes.ES(['%s:%s' % (hostname, port)])
    self.hostname = hostname
    self.cluster_nodes = None
    self.node_id = None

  def get_index_info(self, index_name):
    info = self.conn.status(index_name)
    index_info = info['indices'][index_name]
    docs = index_info['docs']
    size = index_info['index']
    perf = 'deleted_docs=%s num_docs=%s' % (docs['deleted_docs'], docs['num_docs'])
    perf = '%s primary_size_in_bytes=%s' % (perf, size['primary_size_in_bytes'])
    status = 'OK: able to collect|%s' % perf
    return status

  def get_index_list(self):
    info = self.conn.status()['indices']
    return info.keys()

  def get_shard_counts(self, index_name=None):
    # return the number of shards for an index
    # args: index_name [Use none for all indexes]
    res = self.conn.status(index_name)
    res = res['_shards']
    o = 'OK:'
    perf = ''
    for i in res.keys():
      o = '%s %s:%s' % (o, i, res[i])
      perf = '%s %s=%s' % (perf, i, res[i])

    result = '%s|%s' % (o, perf)
    return result

  def getNodeID(self):
    if self.node_id != None:
      return self.node_id

    if self.cluster_nodes == None:
      self.cluster_nodes = self.conn.cluster_nodes()

    nodes = self.cluster_nodes['nodes']
    for i in nodes:
      node_addr = nodes[i]['network']['primary_interface']['address']
      if node_addr == self.hostname:
        self.node_id = i
        return self.node_id

  def get_node_stats(self):
    node = self.getNodeID()
    stats = self.conn.cluster_stats(nodes=[node])['nodes'][node]
    pprint.pprint(stats)

  def get_all_node_stats(self):
#    node = self.getNodeID()
    stats = self.conn.cluster_stats()
    pprint.pprint(stats)

  def cluster_health(self):
    res = self.conn.cluster_health()
    return res

def ParseCommandLine():
  parser = optparse.OptionParser()
  parser.add_option('-H', 
                    help='Hostname of gearman worker',
                    dest='hostname', 
                    action='store', 
                    default=None)
  parser.add_option('-m',
                    help='Mode of operation',
                    dest='mode',
                    action='store',
                    default='shard_counts')
  parser.add_option('--shard_counts',
                    help='do shard counts',
                    dest='mode',
                    action='store_const',
                    const='shard_counts')
  parser.add_option('--index_info',
                    dest='mode',
                    action='store_const',
                    const='index_info')
  parser.add_option('--list_indexes',
                    dest='mode',
                    action='store_const',
                    const='list_indexes')
  parser.add_option('--cluster_health',
                    dest='mode',
                    action='store_const',
                    const='cluster_health')
  parser.add_option('--node_stats',
                    dest='mode',
                    action='store_const',
                    const='node_stats')
  parser.add_option('--all_node_stats',
                    dest='mode',
                    action='store_const',
                    const='all_node_stats')
  parser.add_option('-i',
                    help='Index',
                    dest='index',
                    action='store',
                    default=None)
  return parser

if __name__ == '__main__':
  parser = ParseCommandLine()
  options, args = parser.parse_args()
  hostname = options.hostname
  mode = options.mode
  index = options.index

  # it looks like elastic stores node info by ip address
  # so make sure we are converted to it
  hostname = socket.gethostbyname(hostname)

  a = ElasticConnect(hostname, 9200)
  if mode == 'shard_counts':
    print a.get_shard_counts(index)
    sys.exit(0)
  elif mode == 'index_info':
    print a.get_index_info(index)
    sys.exit(0)
  elif mode == 'list_indexes':
    print a.get_index_list()
  elif mode == 'node_stats':
    a.get_node_stats()
  elif mode == 'all_node_stats':
    a.get_all_node_stats()
  elif mode == 'cluster_health':
    health = a.cluster_health()
    if health['status'] == 'green':
      res = 'OK'
      status = 0
    elif health['status'] == 'yellow':
      res = 'WARNING'
      status = 1
    elif health['status'] == 'red':
      res = 'CRITICAL'
      status = 2
    else:
      res = 'UNKNOWN'
      status = -1

    active_primary_shards = health['active_primary_shards']
    active_shards = health['active_shards']
    cluster_name = health['cluster_name']
    initializing_shards = health['initializing_shards']
    number_of_data_nodes = health['number_of_data_nodes']
    number_of_nodes = health['number_of_nodes']
    relocating_shards = health['relocating_shards']
    unassigned_shards = health['unassigned_shards']

    res = '%s: %s cluster, %s primary shards, %s active shards, %s nodes, %s unassigned, %s initializing, %s relocating' % \
          (res, cluster_name, active_primary_shards,
           active_shards, number_of_nodes, unassigned_shards, 
           initializing_shards, relocating_shards)

    perf = 'active_primary_shards=%s active_shards=%s nodes=%s unassigned_shards=%s initializing_shards=%s relocating_shards=%s' % \
           (active_primary_shards, active_shards,
            number_of_nodes, unassigned_shards, initializing_shards, 
            relocating_shards)
    result = '%s|%s' % (res, perf)
    print result
    sys.exit(status)
