from collections import Counter
from ..utils import ft
from ..env import NLATENCY_INTERVALS
from ..env import MINUTES
from ..env import NLATENCY_COLORS
from ..env import NLATENCY_CODES

from .base import BaseCounter

class LatencyAggregator(BaseCounter):
  id='latencyaggregator'
  base_title="Apache latency"
  
  def __init__(self,title,group):    
    super(LatencyAggregator,self).__init__(title,group)
    self.label="number of pages in %s mins" %MINUTES
    self.counter=Counter(dict([(str(i),0) for i in NLATENCY_INTERVALS]+[('others',0)]))
    
  def update_with(self,datas):
    lat=datas.get_float_latency()/1000000
     
    #aggr evaluate
    if lat is not None and datas.get_bytes()>0 and datas.get_int_code() in NLATENCY_CODES:
      pos=0
      while pos<len(NLATENCY_INTERVALS) and NLATENCY_INTERVALS[pos]<lat:
        pos+=1

      if pos<len(NLATENCY_INTERVALS):
        idx=str(NLATENCY_INTERVALS[pos])
        self.counter[idx]=1+self.counter[idx]
      else:
        self.counter['others']=1+self.counter['others']
            
  def print_data(self, printer, w=None,c=None):
    for threshould in NLATENCY_INTERVALS:
      printer(id="numbers%s"%str(threshould).replace('.',''),
              value=self.counter[str(threshould)],
              label="%s sec"%threshould,
              color=NLATENCY_COLORS[str(threshould).replace('.','')],
              draw="AREASTACK")

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color='FF0000',
            draw="AREASTACK")
