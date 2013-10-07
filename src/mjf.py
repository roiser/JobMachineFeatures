#!/usr/bin/env python

import os, json, socket, urllib2
from datetime import datetime
from optparse import OptionParser

class MJFException(Exception): pass

class mjf:

  def __init__(self, ext=False, pret=False, verb=False, dbg=False, ip='0.0.0.0', timeout=60, tmpfile='mjf.stamp'):
    """
    initialise the class instance and collect machine / job features found on the node
    and store it in the internal data structure. Messages are returned either within the
    returned datastructure (key='messages') if called from the command line or as exceptions
    (ERRORs), or stdout (INFO, DEBUG meesages) in case of importing as a module.
    message levels are: ERROR - INFO - DEBUG 

    options:
    ext: is the script called from the command line (True) or imported (False). This is
         e.g. used when to decide whether to throw exceptions (import) or to return
         messages within the internal data structure (command line).
    pret: enable pretty printing of the output (indentation level=2 with newlines), if set
         to False the json output is returned in one string without newlines
    verb: enable verbose output of the tool, ie. return messages with INFO level or above
    dbg: enable debug output of the tool (lot of info), ie. DEUBG level or above
    ip:  specify the ip address to retrieve the information in case of http retrieval,
         if no ip address is specified the \"magic ip\" address 169.254.169.254 will be tried
    """
    self.varnames = ['MACHINEFEATURES', 'JOBFEATURES'] # names of machine features environment variables
    self.varnameslower = map(lambda x: x.lower(), self.varnames) # lower case versions of the env variable name
    self.httpip = ip                              # ip address for metat data in case of IaaS (openstack)
    if self.httpip == '0.0.0.0' : self.httpip = '169.254.169.254'
    self.httpport = 80
    self.data = {}                                # the machine / job features data structure
    self.ext = ext                                # is the module called from the command line (True) or imported (False)
    self.verb = verb
    self.pret = pret
    self.dbg = dbg
    self.tmpfile = tmpfile
    self.lastcollect = None
    self.timeout = timeout                        # if information retrieved from http, return cache info if called within timeout minutes
    self.indent = None
    if self.pret : self.indent = 2
    self.collect()

  def clean(self):
    """
    clean the data structure, i.e. reset it to an empty dictionary
    """
    self.data = {}

  def collect(self):
    """
    collect the machine / job features information provided
    on this node and store it in the internal data structure
    Note, this function will not previously clean the data
    """
    self._collect()

  def features(self):
    """
    return the machine / job features data collected so far as
    json data structure

    return: json data structure of the features found on the node
            can be empty dictionary if no data was collected / found
    """
    return self.data

  def featureKeys(self):
    """
    return the individual feature names that were collected so far

    return: a dictionary of {'<feature-name>':[<feature-key>,...]}
            can be empty if no data was collected / found so far
    """
    dic = {}
    for var in self.varnameslower :
      if self.data.has_key(var) : dic[var] = self.data[var].keys()
    return dic

  def feature(self, key, feat=''):
    """
    return a value for a given feature-key, optionally a feature namne
    (e.g. MACHINEFEATURES, JOBFEATURES) can be given as a search tip.
    if no optinal feature is given all features will be searched for the key
    and the first occurance will be returned (not deterministic). Otherwise
    the key will only be searched within the feature space given.
    If no key has been found an emtpy string will be returned.
    
    key: the name of the feature key for which the value shall be retrieved (case sensitive)
    feat: the name of the feature (e.g. MACHINEFEATURES) given as optional search hint

    return: value of the feature key or empty string if not found
    """
    if feat :
      if self.data.has_key(feat.lower()) : return self.data[feat.lower()].get(key)
    else :
      for var in self.varnameslower :
        if self.data.has_key(var) and self.data[var].has_key(key) : return self.data[var][key]
    return ''

  def _print(self):
    print json.dumps(self.data, indent=self.indent)

  def _message(self, typ, txt) :
    msg = '%s UTC - %s - %s' % (datetime.utcnow().isoformat(), typ, txt)
    if self.ext :                                 # if called from the command line, return messages within the data structure
      if not self.data.has_key('messages') : self.data['messages'] = [msg]
      else : self.data['messages'].append(msg)
    else :
      if typ == 'ERROR' : raise MJFException(msg) # else in case of error raise an exception
      else: print msg                             # for other message types print them on stdout

  def _error(self, txt) : self._message('ERROR', txt)

  def _info(self, txt) :
    if self.verb or self.dbg : self._message('INFO', txt)

  def _debug(self, txt) :
    if self.dbg : self._message('DEBUG', txt)

  def _addData(self, feature, key, value) :
    if not self.data.has_key(feature) : self.data[feature] = {}
    if value.isdigit() : value = int(value)   # try to convert the value to integer
    else :
      try: value = float(value)               # ... or float
      except ValueError: pass                 # ... or leave as string
    self._debug('Storing value %s for key %s' % (value, key))
    self.data[feature][key] = value

  def _collectViaFile(self):
    self._info('Collecting information from files')
    for var in self.varnames :
      self._debug('Looking for variable %s' % var)
      datakey = var.lower()
      envvar = os.environ[var]
      if os.path.isdir(envvar) :
        self._debug('Collecting information from directory %s' % os.environ[var])
        for f in os.listdir(envvar) :      # for each file in the machine/job features directory
          self._debug('Checking value of file %s in directory %s' % (f, envvar))
          fp = open(envvar + os.sep + f)
          val = fp.read()                           # ... read the file content
          self._debug('Value of file %s is %s' % (f,val))
          fp.close()
          if len(val) and val[-1] == '\n' : val = val[:-1]
          self._addData(datakey, f, val)
      else : self._error('Environment variable %s=%s does not point to a valid directory' % (var, envvar))

  def _serviceHttp(self):
    sock = socket.socket(socket.AF_INET)
    sock.settimeout(1)
    try : sock.connect((self.httpip,self.httpport))
    except Exception,e:
      return False
    return True

  def _getLastAccess(self):
    if self.ext:
      f = open(self.tmpfile, 'r')
      d = f.read()
      f.close()
      return d
    else :
      return self.lastcollect

  def _putLastAccess(self, t):
    if self.ext :
      f = open(self.tmpfile, 'w')
      f.write(t)
      f.close()
    else : self.lastcollect = t
        
  def _collectViaHttp(self):
    now = datetime.now()
    delta = now - self.lastcollect
    if self.lastcollect and delta.seconds < (self.timeout*60) :
      self._putLastAccess(now)
      self._info('Collecting information via http connection')
      data = urllib2.urlopen('http://%s/openstack/latest/meta_data.json'%self.httpip).read()
      jdat = json.loads(data)
      if jdat.has_key('meta') :
        for k in jdat['meta'].keys() :
          ks = k.split('@') 
          if ks[0] == 'mjf' :
            if ks[1] in self.varnameslower : self._addData(ks[1], ks[2], jdat['meta'][k])
    else: self._info('Returning cached information as retrieval was called within interval (%d mins)' % self.timeout)
    

  def _collect(self):
    if not False in map(lambda x: os.environ.has_key(x), self.varnames) : self._collectViaFile() # check if all env variables are there
    elif self._serviceHttp() : self._collectViaHttp() # alternatively try magic IP
    else : self._message('ERROR', 'Cannot find job / machine features information on this node')

  def _run(self):
    self._print()

  
#
# main
#
if __name__ == "__main__" :
  parser = OptionParser()
  parser.add_option('-d', '--debug', action='store_true', default=False, dest='debug', help='enable debug output of the tool')
  parser.add_option('-f', '--tmpfile', action='store', default='mjf.stamp', dest='tmpfile', help='location of the stamp file for http access')  
  parser.add_option('-i', '--ip', action='store', default='0.0.0.0', dest='ip', help='in case of http service set the ip address')
  parser.add_option('-p', '--pretty', action='store_true', default=False, dest='pretty', help='turn on pretty printing of output')
  parser.add_option('-t', '--timeout', action='store', default='60', dest='timeout', help='interval after which new info is returned')
  parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='increase verbosity of the tool')
  (options, args) = parser.parse_args()
  if args : parser.print_help()

  mjf(ext=True, pret=options.pretty, verb=options.verbose, dbg=options.debug, ip=options.ip, timeout=options.timeout, tmpfile=options.tmpfile)._run()   # if the script is called from the command line execute and return data structure
