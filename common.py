
class MetricContainer(object):
  def __init__(self):
    self.vals = []

  def get_metric(self):
    pass

  def append(self, v):
    self.vals.append(v)

class MaxContainer(MetricContainer):
  def get_metric(self):
    if not self.vals:
      return 0
    m = max(self.vals)
    self.vals = []
    return m

class AverageContainer(MetricContainer):
  def get_metric(self):
    if not self.vals:
      return 0
    m = sum(self.vals) / len(self.vals)
    self.vals = []
    return m
    

