#
# Author: david birdsong 2010
# Project URL: http://github.com/davidbirdsong/pygmonlib
#
# License: same as Ganglia
# 

import fcntl
import os
import errno
import subprocess


class GrecordReader(object):

  def __init__(self, fd, record_term_pattern):
    if hasattr(fd, 'fileno'):
      fd = fd.fileno()
    self.fd = int(fd)
    fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
    self._buffer = None
    self._internal_iter = None
    self.record_term_pattern = record_term_pattern

  def fileno(self):
    return self.fd

  def _get_chunk(self):
    data = os.read(self.fd, 4096)
    if self._buffer is not None:
      data = ''.join((self._buffer, data))
      self._buffer = None
    if not data.endswith(self.record_term_pattern):
      s = data.rsplit('\n', 1)
      if len(s) == 2:
        data, self._buffer = s
      else:
        data, self._buffer = '', s
    return data
      
  def _make_iter(self):
    dry_descriptor = False
    data = ''
    split_on = self.record_term_pattern
    while not dry_descriptor:
      try:
        data = self._get_chunk()
      except OSError, e:
        if e.errno != errno.EAGAIN: raise
        dry_descriptor = True
        continue
      for record in data.split(self.record_term_pattern):
        # return only full strings
        if record: 
          yield record
    self._internal_iter = None
    # yield keyword should handle this, but explicit is better than implicit
    raise StopIteration

  def record(self):
    """
    initialize internal iterator if None
    does not exhaust iterator, saves it
    """
    i = self._internal_iter
    if i is None:
      i = self._make_iter()

    try:
      record = i.next()
      if self._internal_iter is None:
        self._internal_iter  = i
    except StopIteration:
      record = None
    
    return record

  def records(self):
    """
    initialize internal iterator if None
    exhaust the iterator
    """
    i = self._internal_iter
    if i is None:
      i = self._make_iter()

    for line in i:
      yield line 

class GlineReader(GrecordReader):
  def __init__(self, fd):
    GrecordReader.__init__(self, fd, '\n')

  def readline(self):
    return self.record()

  def readlines(self):
    return self.records()

class GlogFileTailer(GlineReader):
  def __init__(self, logfile):
    cmd = 'tail -f %s' % logfile
    cmd = cmd.split()
    self.proc = proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    GlineReader.__init__(self, proc.stdout)

  def __del__(self):
    os.kill(self.proc.pid, 15)
