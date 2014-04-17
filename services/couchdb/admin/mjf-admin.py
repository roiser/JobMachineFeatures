#!/usr/bin/env python

VERSION='0.0.1'

from optparse import OptionParser
import sys, json, urllib, httplib

class log :
  def __init__(self, dbg=False, inf=True): 
    self.dbg = dbg
    self.inf = inf
    self.module = __file__

  def message(self, typ, txt, ext=False):
    print '%s: %s: %s' % (self.module.ljust(len(self.module)), typ.ljust(7), txt)
    if ext : sys.exit(1)

  def debug(self, txt) : 
    if self.dbg: self.message('DEBUG', txt)

  def info(self, txt) : 
    if self.inf: self.message('INFO', txt)

  def warning(self, txt) : self.message('WARNING', txt)

  def error(self, txt, ext=True) : self.message('ERROR', txt, ext)
    

class mjfAdmin :

  def __init__(self, server, port, database, bulk, selkey, value, logi=None):
    self.log = log()
    if logi: self.log = logi
    self.server = server
    self.port = port
    self.database = database
    self.bulk = bulk
    self.selkey = selkey
    self.value = value
    self.fullserver = 'http://%s:%s' % (self.server, self.port)
    self.headers = {"Content-type": "application/json"}

  def _httprequest(self, typ, url, doc='', jsn=True) : 
    conn = httplib.HTTPConnection(self.server, port=self.port)
    conn.request(typ, '/'+url, doc, self.headers)
    ret = conn.getresponse()
    self.log.debug('Status %s, Response: %s' % (ret.status, ret.reason))
    retval = ret.read()
    conn.close()
    if jsn : return json.loads(retval)
    else : return retval

  def _dbinstalled(self): 
    self.log.debug('Checking if database is installed')
    data = self._httprequest('GET', '_all_dbs')
    self.log.debug('Databases found: %s' %  data)
    if self.database in data : return True
    else : return False    

  def _installdb(self) :
    if not self._dbinstalled():
      self.log.info('Installing database %s at server %s' % (self.database, self.fullserver))
      data = self._httprequest('PUT', self.database, jsn=False)
      self.log.info('Data: %s' % data)
    else: 
      self.log.warning('Database %s already installed on server %s' % (self.database, self.fullserver))

  def _removedb(self) : 
    if self._dbinstalled(): 
      self.log.info('Droping database %s from server %s' % (self.database, self.fullserver))
      data = self._httprequest('DELETE', self.database, jsn=False)
      self.log.info('Data: %s' % data)
    else: 
      self.log.warning('Database %s not found on server %s' % (self.database, self.fullserver))

  def _checkdb(self) :
    self.log.info('Checking connection to couchdb server %s' % (self.fullserver))
    info = self._httprequest('GET', '')
    if info.has_key('couchdb') and info['couchdb'] == 'Welcome' : 
      self.log.info('Successful contacting server %s, response %s' % (self.fullserver, str(info)))
    else :
      self.log.error('Cannot connect to server %s, return message: %s' % (self.fullserver, str(info)))
    dbs = self._httprequest('GET', '_all_dbs')
    self.log.info('Databases installed: %s' % dbs)

  def _put(self) : 
    self.log.debug('Putting document(s) on database %s at server %s' % (self.database, self.fullserver))

  def _get(self) : 
    self.log.debug('Getting document(s) from database %s at server %s' % (self.database, self.fullserver))

  def _delete(self) : 
    self.log.debug('Deleting document(s) from database %s at server %s' % (self.database, self.fullserver))

  def _version(self): 
    print VERSION
    sys.exit(0)


if __name__ == '__main__' : 
  actions = ['installdb','removedb','checkdb','version','put','get','delete']
  parser = OptionParser()
  parser.add_option('-q', '--quiet', action='store_false', default=True, dest='quiet', help='only print warning and error messages')
  parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='increase verbosity of output')
  parser.add_option('-s', '--server', action='store', default='wlcg-mjf', dest='server', help='host name of the key value store (default="wlcg-mjf")')
  parser.add_option('-p', '--port', action='store', default='5984', dest='port', help='port to access the web interface of the store (default=5984)')
  parser.add_option('-d', '--database', action='store', default='machinejobfeatures', dest='database', help='database name storing the features (default="machinejobfeatures")')
  parser.add_option('-b', '--bulk', action='store_true', default='False', dest='bulk', help='execute a bulk operation on multiple documents')

  
  action = ''
  selkey = ''
  value = ''

  (options,args) = parser.parse_args()
  if not len(args) or args[0] not in actions : 
    parser.print_help()
    sys.exit(1)
  else : action=args[0]

  if action == 'put' :
    if len(args) != 3 : 
      parser.print_help()
      sys.exit(1)
    else :  
      selkey = args[1]
      value = args[2]
  elif action in ('get','delete') :
    if len(args) != 2 : 
      parser.print_help()
      sys.exit(1)
    else: 
      selkey = args[1]
  elif action in ('installdb', 'removedb', 'checkdb', 'version') : 
    if len(args) != 1 : 
      parser.print_help()
      sys.exit(1)

  logi = log(options.verbose,options.quiet)

  mad = mjfAdmin(options.server, options.port, options.database, options.bulk, selkey=selkey, value=value, logi=logi)
  if '_'+action in dir(mad) : eval('mad._'+action+'()')
  


# Setup of the instance
# 1 deploy the node
# 2 install couchdb rpm
# 3 /etc/couchdb/local.ini
#   bind_address = 0.0.0.0
# 4 /etc/init.d/couchdb start
# 5 


# setup
# drop
# check
#
# put <key> <value>
# get <key>
# delete <key>
#
# bulk put <selection> <value>
# bulk get <selection>
# bulk delete <selection>
