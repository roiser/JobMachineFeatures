#!/usr/bin/env python

"""
unit tests for the mjf tool, both cli and python module imported
run like \"python mjf-unit.py\"
"""

import os, sys, unittest, json

class Environ():

  def __init__(self):
    self.pwd = os.path.dirname(os.path.realpath(__file__.__str__()))
    self.pkd = os.path.dirname(self.pwd)
    self.mdd = self.pkd+os.sep+'src'+os.sep+'python-mjf'
    self.pyt_setup = False
    self.cmd_setup = False
    self.mjs_setup = False
    self.mjp_setup = False
    self.features = {'machinefeatures': ['hs06', 'jobslots', 'log_cores', 'phys_cores'],
                     'jobfeatures' : ['disk_limit_GB', 'jobstart_secs', 'wall_limit_secs',
                                      'cpu_limit_secs', 'cpu_limit_secs_lrms', 'allocated_CPU',
                                      'mem_limit_MB']
                     }

  def setup(self, py=False, cmd=False, mjf=False, mjfp=False):
    if mjfp :
      self.mjp_setup = True
      os.environ['MACHINEFEATURES'] = self.pwd+os.sep+'m'
      os.environ['JOBFEATURES'] = self.pwd+os.sep+'j'
    if mjf :
      self.mjs_setup = True
      os.putenv('MACHINEFEATURES', self.pwd+os.sep+'m')
      os.putenv('JOBFEATURES', self.pwd+os.sep+'j')
    if py :
      self.pyt_setup = True
      sys.path.append(self.mdd)
    if cmd :
      self.cmd_setup = True
      os.environ['PATH'] += os.pathsep + self.mdd

  def tearDown(self):
    if self.pyt_setup :
      sys.path = [ x for x in sys.path if x != self.mdd ]
      self.pyt_setup = False
    if self.cmd_setup :
      os.environ['PATH'] = os.pathsep.join([ x for x in os.environ['PATH'].split(os.pathsep) if x != self.mdd ])
      self.cmd_setup = False
    if self.mjs_setup or self.mjp_setup :
      os.unsetenv('MACHINEFEATURES')
      os.unsetenv('JOBFEATURES')
      self.mjs_setup = False
      self.mjp_setup = False


class MJFTestPythonModule(unittest.TestCase) :

  def setUp(self):
    self.env = Environ()

  def test_import(self):
    self.env.setup(py=True)
    import mjf
    self.env.tearDown()

  def test_nofeatures(self):
    self.env.setup(py=True)
    from mjf import mjf, MJFException
    try: m = mjf()
    except MJFException,e : self.assertTrue(e.__str__().find('ERROR'))
    self.env.tearDown()

  def tearDown(self):
    self.env.tearDown()

class MJFTestPythonAPI(unittest.TestCase) :

  def setUp(self):
    self.env = Environ()
    self.env.setup(py=True, mjfp=True)
    from mjf import mjf
    self.m = mjf()

  def test_features(self):
    d = self.m.features()
    self.assertTrue(d)
    for f in self.env.features.keys() :
      self.assertTrue(d.has_key(f))
      for k in self.env.features[f] :
        self.assertTrue(d[f].has_key(k))

  def test_clean(self):
    d = self.m.features()
    self.assertTrue(d)
    self.m.clean()
    d = self.m.features()
    self.assertFalse(d)

  def test_collect(self):
    d1 = self.m.features()
    self.assertTrue(d1)
    self.m.clean()
    d2 = self.m.features()
    self.assertFalse(d2)
    self.m.collect()
    d3 = self.m.features()
    self.assertEquals(d1,d3)

  def test_keys(self):
    k = self.m.featureKeys()
    for f in self.env.features.keys() :
      self.assertTrue(k.has_key(f))
      for x in k[f] : self.assertTrue(x in self.env.features[f])

  def test_feature(self):
    f1 = self.m.feature('jobslots', 'MACHINEFEATURES')
    self.assertEquals(f1, 18)
    f2 = self.m.feature('jobslots', 'JOBFEATURES')
    self.assertFalse(f2)
    f3 = self.m.feature('jobslots')
    self.assertEquals(f3, 18)
    f4 = self.m.feature('notexistingfeature')
    self.assertFalse(f4)

  def tearDown(self):
    self.env.tearDown()


class MJFTestCommandline(unittest.TestCase) :

  def setUp(self):
    self.env = Environ()

  def test_read(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen("mjf.py").read()[:-1]
    self.assertNotEquals(r, '')
    self.env.tearDown()

  def test_content(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen("mjf.py").read()[:-1]
    self.assertTrue(r)
    d = json.loads(r)
    for f in self.env.features.keys() :
      self.assertTrue(d.has_key(f))
      for k in self.env.features[f] :
        self.assertTrue(d[f].has_key(k))
    self.env.tearDown()

  def test_notwork(self):
    self.env.setup(cmd=True)
    r = os.popen('mjf.py -i 0.0.0.1').read()[:-1]
    d = json.loads(r)
    self.assertTrue(d.has_key('messages'))
    self.env.tearDown()

  def test_optionverbose(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen('mjf.py -v').read()[:-1]
    self.assertTrue(r)
    self.assertEquals(r.find('\n'), -1)
    self.assertNotEquals(r.find(' - INFO - '), -1)
    self.assertEquals(r.find(' - DEBUG - '), -1)
    self.env.tearDown()

  def test_optiondebug(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen('mjf.py -d').read()[:-1]
    self.assertTrue(r)
    self.assertEquals(r.find('\n'), -1)
    self.assertNotEquals(r.find(' - INFO - '), -1)
    self.assertNotEquals(r.find(' - DEBUG - '), -1)
    self.env.tearDown()

  def test_optionpretty(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen('mjf.py -p').read()[:-1]
    self.assertTrue(r)
    self.assertNotEquals(r.find('\n'), -1)
    self.assertEquals(r.find(' - INFO - '), -1)
    self.assertEquals(r.find(' - DEBUG - '), -1)
    self.env.tearDown()

  def test_optionprettyverbose(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen('mjf.py -p -v').read()[:-1]
    self.assertTrue(r)
    self.assertNotEquals(r.find('\n'), -1)
    self.assertNotEquals(r.find(' - INFO - '), -1)
    self.assertEquals(r.find(' - DEBUG - '), -1)
    self.env.tearDown()

  def test_optionprettydebug(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen('mjf.py -p -d').read()[:-1]
    self.assertTrue(r)
    self.assertNotEquals(r.find('\n'), -1)
    self.assertNotEquals(r.find(' - INFO - '), -1)
    self.assertNotEquals(r.find(' - DEBUG - '), -1)
    self.env.tearDown()

  def test_optionverbosedebug(self):
    self.env.setup(cmd=True, mjf=True)
    r = os.popen('mjf.py -v -d').read()[:-1]
    self.assertTrue(r)
    self.assertEquals(r.find('\n'), -1)
    self.assertNotEquals(r.find(' - INFO - '), -1)
    self.assertNotEquals(r.find(' - DEBUG - '), -1)
    self.env.tearDown()

  def tearDown(self):
    self.env.tearDown()

if __name__ == '__main__' :
  testclasses = [MJFTestPythonModule, MJFTestPythonAPI, MJFTestCommandline]
  alltests = unittest.TestSuite(map(lambda x : unittest.TestLoader().loadTestsFromTestCase(x), testclasses))
  unittest.TextTestRunner(verbosity=2).run(alltests)
