#!/usr/bin/env python

import os, json
from datetime import datetime

class mjf:

  def __init__(self):
    self.varnames = ['MACHINEFEATURES', 'JOBFEATURES'] # names of machine features environment variables
    self.magicip = '169.254.169.254' # magic ip address in case of IaaS / openstack
    self.data = {} # the machine / job features data structure
    self.ext = False   # is the module called from the command line (True) or imported (False)

  def _print(self):
    print json.dumps(self.data)

  def _message(self, typ, txt) :
    msg = '%s UTC - %s - %s' % (datetime.utcnow().isoformat(), typ, txt)
    if self.ext :
      if not self.data.has_key('messages') : self.data['messages'] = [msg]
      else : self.data['messages'].append(msg)
    else : raise msg

  def _collectViaFile(self):
    for var in self.varnames :
      datakey = var.lower()
      if not self.data.has_key(datakey) : self.data[datakey] = {}
      for f in os.listdir(os.environ[var]) :
        fp = open(os.environ[var] + os.sep + f)
        val = fp.read()
        fp.close()
        if val[-1] == '\n' : val = val[:-1]
        if val.isdigit() : val = int(val)
        else :
          try: val = float(val)
          except ValueError: pass
        self.data[datakey][f] = val

  def _isVMNode(self):
    pass

  def _pingMagicIP(self):
    pass
        
  def _collectViaHttp(self):
    pass

  def _collect(self):
    if not False in map(lambda x: os.environ.has_key(x), self.varnames) : self._collectViaFile()
    elif self._isVMNode() and self._pingMagicIP() : self._collectViaHttp()
    else : self._message('ERROR', 'Cannot find job / machine features information on this node')

  def clean(self):
    self.data = {}

  def collect(self):
    self._collect()

  def run(self, ext=False):
    self.ext = ext
    self._collect()
    self._print()

  



if __name__ == "__main__" : mjf().run(ext=True)
