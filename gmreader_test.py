#!/usr/bin/python

import subprocess
import unittest
import tempfile
import os
import re 
import sys
import gmreader
import time

DEFAULT_TAIL_LINES = 10
LOG_LINE = '''%i 192.168.1.1 - - [24/Sep/2010:22:07:53 -0400] "GET /index.html HTTP/1.1" 200 11213 "-" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.9) Gecko/20100824 Firefox/3.6.9"'''

CMD = 'tail -f %s'

log_re = re.compile(r'^[0-9]+ %s'%  LOG_LINE.split(None, 1)[-1])

class TestGLineReader(unittest.TestCase):
      
  def write_lines(self, fd, num_lines):
    # l('writing to %s' % fd.name)
    l_line = LOG_LINE
    
    fd.write('%s \n' %  '\n'.join(l_line % n for n in xrange(num_lines)))
    # print  '\n'.join(l_line % n for n in xrange(num_lines))
    # we want tail to get scheduled by the os so as to fill the pipe
    time.sleep(1)
    fd.flush()

  def setUp(self):
    # l('calling setup ')
    self.out_file = tempfile.NamedTemporaryFile(mode='w')
    self.write_lines(self.out_file, DEFAULT_TAIL_LINES * 10)
    cmd = CMD % self.out_file.name
    cmd = cmd.split()
    self.proc = proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    self.gread = gmreader.GlineReader(proc.stdout)

  def tearDown(self):
    os.kill(self.proc.pid, 15)
    self.out_file.close()
        
  def test_initial_data(self):  
    time.sleep(1)
    self.assertEqual(len(list(self.gread.readlines())), DEFAULT_TAIL_LINES)

  def test_readline(self):  
    # empty out file first
    list(self.gread.readlines())
    list(self.gread.readlines())
    # 90 is about a 4k buffer  page
    self.write_lines(self.out_file, 90)
    line = self.gread.readline()
    
    self.assertEqual(line, LOG_LINE % 0)
    # self.assertEqual(line, LOG_LINE)

  def test_stopIteration(self):
    # all these sleeps to help get another process like 'tail' 
    # to get scheduled and read all the data and send it through the pipe 
    list(self.gread.readlines())
    time.sleep(2)
    list(self.gread.readlines())
    time.sleep(2)
    g = self.gread.readlines()
    time.sleep(2)
    self.assertRaises(StopIteration, g.next)

if __name__ == '__main__':
    unittest.main()
