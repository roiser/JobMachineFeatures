#!/usr/bin/env python

VERSION='0.0.1'

from optparse import OptionParser, IndentedHelpFormatter
import sys, json, urllib, httplib, os, base64, getpass

# class PlainHelpFormatter(IndentedHelpFormatter):
#     def format_description(self, description):
#         if description:
#             return description + "\n"
#         else:
#             return ""
#     def format_epilog(self, epilog):
#         if epilog:
#             return epilog + "\n"
#         else:
#             return ""

class log :
  def __init__(self, dbg=False, inf=True): 
    self.dbg = dbg
    self.inf = inf
    self.module = __file__

  def message(self, typ, txt, nwl, ext=False):
    nlstr = ''
    if nwl : nlstr = '\n'
    sys.stdout.write('%s: %s: %s%s' % (self.module.ljust(len(self.module)), typ.ljust(7), txt, nlstr))
    #print '%s: %s: %s' % (self.module.ljust(len(self.module)), typ.ljust(7), txt)
    if ext : sys.exit(1)

  def debug(self, txt, nwl=True) :
    if self.dbg: self.message('DEBUG', txt, nwl)

  def info(self, txt, nwl=True) :
    if self.inf: self.message('INFO', txt, nwl)

  def warning(self, txt, nwl=True) : self.message('WARNING', txt, nwl)

  def error(self, txt, nwl=True, ext=True) : self.message('ERROR', txt, nwl, ext)
    

class mjfAdmin :

  def __init__(self, server, port, database, user, args, selkey, value, logi=None):
    self.log = log()
    if logi: self.log = logi
    self.server = server
    self.port = port
    self.database = database
    self.selkey = selkey
    self.value = value
    self.user = user
    self.pwd = ''
    self.pwfile = '.wlcgmjfadmin.pw'
    self.arguments = args
    self.fullserver = 'http://%s:%s' % (self.server, self.port)
    self._getPassword()
    authb64 = base64.encodestring('%s:%s'%(self.user, self.pwd)).replace('\n','')
    self.headers = {"Content-type": "application/json", "Accept-Encoding": "*", "Authorization": "Basic %s"%authb64 }

  def _getPassword(self) :
    if self.pwd : return
    homdir = os.path.expanduser('~')
    pwfullfile = homdir+os.sep+self.pwfile
    if os.path.isfile(pwfullfile) :
      f = open(pwfullfile)
      self.pwd = f.read().replace('\n','')
      f.close()
    else :
      self.log.info('Please provide password for admin user:', nwl=False)
      self.pwd = getpass.getpass('')
      f = open(pwfullfile, 'w')
      f.write(self.pwd)
      f.close()
      self.log.debug('Admin password written to ' + pwfullfile)

  def _strToJson(self, instr) :
    # ugly hack, this needs to be fixed
    newstr = str(instr).replace("u'", "'").replace("'", '"').replace("True","true").replace("False","false")
    js = None
    try : 
      js = json.loads(newstr)
    except Exception, e: 
      self.log.error('conversion of string %s, %s' % (newstr, e))
    return js

  def _httprequest(self, typ, url, doc='', headeradd={}, jsn=True) : 
    header = dict(self.headers.items() + headeradd.items())
    conn = httplib.HTTPConnection(self.server, port=self.port)
    if self.log.dbg : conn.set_debuglevel(99)
    try: 
      conn.request(typ, '/'+url, doc, header)
      ret = conn.getresponse()
    except Exception, e: self.log.error(e)
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
    if self.database in dbs : self.log.info('Database %s installed' % self.database)
    else : self.log.error('Database %s not installed on server, installed DBs are %s' % ( self.database, dbs))

  def _put(self) : 
    key = self.arguments[1]
    value = self.arguments[2]
    self.log.debug('Putting document(s) %s on database %s at server %s' % (key, self.database, self.fullserver))
    inf = self._httprequest('PUT', self.database + os.sep + key, doc=value)
    jinfo = self._strToJson(inf)
    if jinfo.has_key('error') : self.log.error('Could not create post document %s, error=%s, reason=%s' % (key, jinfo.get('error'), jinfo.get('reason')))
    else: self.log.info('Put successful '+ str(jinfo))

  def _get(self) : 
    key = self.arguments[1]
    self.log.debug('Getting document(s) from database %s at server %s' % (self.database, self.fullserver))
    inf = self._httprequest('GET', self.database + os.sep + key)
    jinfo = self._strToJson(inf)
    if jinfo.has_key('error') : self.log.error('Cannot get document %s, error=%s, reason=%s' % (key, jinfo.get('error'), jinfo.get('reason')))
    else: self.log.info('Get successful' + str(jinfo))

  def _delete(self) : 
    key = self.arguments[1]
    self.log.debug('Deleting document(s) %s from database %s at server %s' % (key, self.database, self.fullserver))
    inf = self._httprequest('GET', self.database + os.sep + key)
    jinf = self._strToJson(inf)
    if jinf.has_key('_rev'):
      rev = jinf['_rev'] 
      self.log.debug('Deleting object with key %s and revision %s' % ( key, rev ))
      inf2 = self._httprequest('DELETE', self.database + os.sep + key, headeradd={"If-Match":rev})
      jinf2 = self._strToJson(inf2)
      if jinf2.has_key('error') : self.log.error('Cannot delete document %s, error=%s, reason=%s' % (key, jinf2.get('error'), jinf2.get('reason')))
      else : self.log.info('Delete successful '+ str(jinf2))
    elif jinf.has_key('error') : 
      self.log.error('Cannot find revision for document %s, error=%s, reason=%s' % (key, jinf['error'], jinf.get('reason')))

  def _version(self): 
    print VERSION
    sys.exit(0)


if __name__ == '__main__' : 
  actions = ['installdb','removedb','checkdb','version','put','get','delete']
  usage = 'usage: %prog [options] [put <key> <value>] | [ get | delete <key>] | [ installdb | removedb | checkdb | version ]'
  desc = """Arguments:\n
   put:\n
   get:\n
   delete:\n 
   installdb:\n 
   removedb:\n
   checkdb:\n
   version:
"""
  parser = OptionParser(usage=usage) #, description=desc)
  parser.add_option('-d', '--database', action='store', default='machinejobfeatures', dest='database', help='database name storing the features (default="machinejobfeatures")')
  parser.add_option('-p', '--port', action='store', default='5984', dest='port', help='port to access the web interface of the store (default=5984)')
  parser.add_option('-q', '--quiet', action='store_false', default=True, dest='quiet', help='only print warning and error messages')
  parser.add_option('-s', '--server', action='store', default='wlcg-mjf.cern.ch', dest='server', help='host name of the key value store (default="wlcg-mjf")')
  parser.add_option('-u', '--user', action='store', default='admin', dest='user', help='admin user name on couchdb (default="admin")')
  parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='increase verbosity of output')
  
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

  mad = mjfAdmin(options.server, options.port, options.database, options.user, args, selkey=selkey, value=value, logi=logi)
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


#  ./mjf-admin.py  put 113.3.0.3 '{"machinefeatures": {"hs06": 9.0999999999999996, "jobslots": 9, "shutdowntime": 1398790803.78, "log_cores": 8, "shutdown_command": "shutdown -h now", "phys_cores": 15}, "jobfeatures": {"disk_limit_GB": 138, "jobstart_secs": 1398783794.78, "cpufactor_lrms": 9.9900000000000002, "cpu_limit_secs": 65798, "cpu_limit_secs_lrms": 85504, "allocated_CPU": 6, "mem_limit_MB": 4406, "wall_limit_secs_lrms": 80541, "wall_limit_secs": 76355, "shutdowntime_job": 1398793344.78}}'
#
# ./mjf-admin.py: INFO   : Put successful {u'ok': True, u'rev': u'1-b50910ed8b66afde135d7137dbee6266', u'id': u'113.3.0.3'}
