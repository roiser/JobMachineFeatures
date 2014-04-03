#!/usr/bin/python

from urllib import urlopen, urlretrieve
import tarfile, sys, os

class mjfprobe :

  def __init__(self):
    self.version = '0.0.1'
    self.logs = []
    self.mjfrepo = 'http://sroiser.web.cern.ch/sroiser/mjf/'
    self.importfrom = ''
    self.exitcode = 0
    self.statuscodes = {'OK': 0, 'INFO': 0, 'WARNING': 1, 'ERROR': 3}
    self.codesstatus = {}
    for x in self.statuscodes.keys(): self.codesstatus[self.statuscodes[x]] = x
    self.info('mjf SAM probe version: %s' % self.version)
    self.features = {'machinefeatures': ['hs06', 'jobslots', 'log_cores', 'phys_cores'],
                     'jobfeatures' : ['disk_limit_GB', 'jobstart_secs', 'wall_limit_secs',
                                      'cpu_limit_secs', 'cpu_limit_secs_lrms', 'allocated_CPU',
                                      'mem_limit_MB']
                     }


  # generic test functions
  def test_range(self, val, upper, lower):
    if val <= upper and val >= lower :
      self.info('value %s within range [%s,%s]' % (val, lower, upper))
    else :
      self.warning('value %s outside range [%s,%s]' % (val, lower, upper))
  
  def test_range_float(self, val, upper, lower):
    try :
      fval = float(val)
      self.test_range(val, upper, lower)
    except:
      self.warning('cannot convert value %s to float' % val)

  def test_range_int(self, val, upper, lower):
    try :
      ival = int(val)
      self.test_range(val, upper, lower)
    except:
      self.warning('cannot convert value %s to int' % val)

  # test features section
  def test_hs06(self, val):
    upper = 1.0
    lower = 20.0
    self.test_range_float(val, upper, lower)

  def test_jobslots(self, val):
    upper = 100
    lower = 1
    self.test_range_int(val, upper, lower) 

  def test_log_cores(self, val):
    upper = 100
    lower = 1
    self.test_range_int(val, upper, lower)
  
  def test_phys_cores(self, val):
    upper = 100
    lower = 1
    self.test_range_int(val, upper, lower)
  
  def test_disk_limit_GB(self, val):
    upper = 1000.0
    lower = 1.0
    self.test_range_float(val, upper, lower)
  
  def test_jobstart_secs(self, val):
    self.info('no test, value: %i' % val)
  
  def test_wall_limit_secs(self, val):
    self.info('no test, value: %i' % val)
  
  def test_cpu_limit_secs(self, val):
    self.info('no test, value: %i' % val)
  
  def test_cpu_limit_secs_lrms(self, val):
    self.info('no test, value: %i' % val)
  
  def test_allocated_CPU(self, val):
    upper = 128
    lower = 1
    self.test_range_int(val, upper, lower)
  
  def test_mem_limit_MB(self, val):
    upper = 8192
    lower = 1024
    self.test_range_int(val, upper, lower)
  
  
  # other module functions


  def finalize(self) :
    print '%s, %s (v %s)' % (self.codesstatus[self.exitcode], ' '.join(self.logs[-1].split(':')[1:]), self.version)
    for log in self.logs : print log
    sys.exit(self.exitcode)

  def log(self, type, txt):
    self.logs.append('%s: %s' % (type,txt))
    self.exitcode = self.exitcode | self.statuscodes[type.strip()]
    if self.exitcode == self.statuscodes['ERROR'] : self.finalize()

  def info(self, txt)     : self.log('INFO   ', txt)

  def warning(self, txt)  : self.log('WARNING', txt)
  
  def error(self, txt)    : self.log('ERROR  ', txt)


  def try_import(self):
    try:
      import mjf
      self.importfrom = 'system'
      self.info('mjf imported from system level')
      return True
    except ImportError:
      self.warning('mjf not installed on the system level')
      mjfvers = urlopen(self.mjfrepo+'version').read().split('\n')[0]
      tarname = 'mjf-%s.tar.gz' % mjfvers
      urlretrieve('%s%s'%(self.mjfrepo, tarname), tarname)
      tf = tarfile.open(tarname)
      tf.extractall()
      try :
        import mjf
        self.importfrom = 'external'
        self.info('mjf imported from user land')
        return True
      except ImportError:
        self.error('cannot import downloaded mjf')
    return False

  def test_feature(self, feature, value):
    try:
      self.info('start testing feature %s' % feature)
      fun = getattr(self, 'test_'+feature)
      fun(value)
      self.info('end testing feature %s' % feature)
    except AttributeError :
      self.warning('don\'t know how to test feature %s' % feature)

  def test_feature_file(self, featurefile):
    val = None
    if os.path.isfile(featurefile) :
      f = open(featurefile, 'r')
      val = f.read()
      f.close()
      self.test_feature(os.path.basename(featurefile), val)
    else :
      self.warning('feature file %s cannot be opened' % featurefile)

  def test_features_with_mjf(self) :
    self.info('testing features with the mjf tool')
    from mjf import mjf, MJFException
    m = mjf()
    try : 
      m.collect()
      features = m.features()
      self.info(features)
      for featureclass in self.features.keys() :
        self.info('testing %s' % featureclass)
        for feature in self.features[featureclass] : self.test_feature(feature, features[featureclass][feature])
    except MJFException, e:
      self.warning('collecting features failed with message "%s"' % e)

  def test_features_standalone(self):
    self.info('testing features standalone without mjf client')
    for var in ['MACHINEFEATURES', 'JOBFEATURES']:
      if os.environ.has_key(var) :
        val = os.environ[var]
        self.info('environment variable %s found, value = %s' % ( var, val))
        features = os.listdir(val)
        if features :
          self.info('%s provides features for %s' % (var, features))
          map(lambda x: self.test_feature(val+os.path.sep+x), features)
        else:
          self.warning('directory %s is empty' % val)
      else :
        self.warning('environment variable %s not found' % var)

  def run(self):
    if self.try_import() : self.test_features_with_mjf()
    else : self.test_features_standalone()
    self.finalize()


if __name__ == '__main__' :
  mp = mjfprobe()
  mp.run()
