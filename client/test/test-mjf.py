#!/usr/bin/env python

from mjf import mjf,MJFException

m = mjf()
try :
  m.collect()
  print m.features()
except MJFException, e:
  print e
