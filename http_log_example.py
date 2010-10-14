import gmreader 
import sys
import time

HTTPCodeHandler = None

class HttpCodes(object):
  def __init__(self, logfile, collect_interval, metric_group):
  
    self.descriptors = []
    descriptor = {
      'call_back': self.get_metric,
      'time_max': collect_interval,
      'value_type': 'uint',
      'units': 'ticks',
      'slope': 'both',
      'format': '%u',
      'groups': metric_group,
      'name' : 'http_500' 
    }
    self.descriptors.append(descriptor)
    self.input = gmreader.GlogFileTailer(logfile)
    self.http_codes = {}

  def _parse_http_code(self, line):
    """
    NOT A GOOD LINE PARSE EXAMPLE
    parse out http code from this line 
    127.0.0.1 - - [24/Sep/2010:21:16:17 -0400] "GET /foo HTTP/1.1" 404 169 "-" "curl/7.20.0 (x86_64-redhat-linux-gnu) libcurl/7.20.0 NSS/3.12.6.2 zlib/1.2.3 c-ares/1.7.0 libidn/1.16 libssh2/1.2.4"

    return http code and http code class 
    """
    code = int(line.split('"')[2].split()[0])
    try:
      return (code, 'http_%i' % (code - code % 100))
    except TypeError:
      print line
      raise

  def return_descriptors(self):
    return self.descriptors

  def get_metric(self, name):
    # input object will return lines written to file since 
    # last read
    for line in self.input.readlines():
      for code in self._parse_http_code(line):
        self.http_codes.setdefault(code, 0)
        self.http_codes[code] += 1
    value = self.http_codes.get(name, 0)
    self.http_codes[name] = 0
    return value

def metric_init(params):
  collect_interval = params.get('collect_interval', 15)
  metric_group = params.get('metric_group', 'HTTP Codes')
  logfile = params.get('logfile')
  if logfile is None:
    print >> sys.stderr, 'Missing logfile param'
    return []

  global HTTPCodeHandler
  HTTPCodeHandler = HttpCodes(logfile, collect_interval, metric_group)
  return HTTPCodeHandler.return_descriptors()

  
def metric_cleanup():
  global HTTPCodeHandler
  del HTTPCodeHandler
  
if __name__ == '__main__':

  params = {}
  params['logfile'] = sys.argv[1]
  params['metric_group'] = 'X-Gmond-Module-HTTP500-TEST'
  params['collect_interval'] = collect_interval = 30
  descriptors = metric_init(params)
  while True:
    for d in descriptors:
      call_back = d['call_back']
      mname = d['name']
      v = call_back(mname)
      print '%s -> %i' % ( mname, v)
    time.sleep(collect_interval)
    print '\n'
