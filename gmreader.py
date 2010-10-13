import fcntl
import os
import errno
import subprocess


class GrecordReader(object):

  def __init__(self, fd, record_terminate_pattern):
    if hasattr(fd, 'fileno'):
      fd = fd.fileno()
    self.fd = int(fd)
    self._runt = None
    fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
    self._internal_iter = None
    self.split_pattern = split_pattern
    self.record_term_pattern = record_terminate_pattern

  def fileno(self):
    return self.fd

  def _get_chunk(self):
    data = os.read(self.fd, 4096)
    if self._runt is not None:
      data = ''.join((self._runt, data))
      self._runt = None
    if not data.endswith(self.record_term_pattern):
      s = data.rsplit('\n', 1)
      if len(s) == 2:
        data, self._runt = s
      else:
        data, self._runt = '', s
       
    return data
      
  def _make_iter(self):
    dry_pipe = False
    data = ''
    while not dry_pipe:
      try:
        data = self._get_chunk()
      except OSError, e:
        if e.errno != errno.EAGAIN: raise
        dry_pipe = True
        continue
      
      for line in data.split('\n'):
        if line: yield line

    self._internal_iter = None
      
  def readline(self):
    i = self._internal_iter
    if i is None:
      i = self._make_iter()

    try:
      line = i.next()
      if self._internal_iter is None:
        self._internal_iter  = i
    except StopIteration:
      line = None
    
    return line

  def readlines(self):
    i = self._internal_iter
    if i is None:
      i = self._make_iter()

    for line in i:
      yield line 

class GlineReader(GrecordReader):

class GlogTailer(GlineReader):
  def __init__(self, logfile):
    cmd = 'tail -f %s' % logfile
    cmd = cmd.split()
    self.proc = proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    GlogReader.__init__(self, proc.stdout)

      
  def __del__(self):
    os.kill(self.proc.pid, 15)

