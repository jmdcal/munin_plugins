from collections import Counter
from utils import ft
from etc.env import INTERVALS
from etc.env import MINUTES

from base import BaseCounter

class LatencyAggregator(BaseCounter):
  id='latencyaggregator'
  
  def __init__(self,title,group):    
    super(LatencyAggregator,self).__init__("Nginx latency: %s"%title,group)
    self.label="number of pages"
    self.counter=Counter(dict([(str(i),0) for i in INTERVALS]+[('others',0)]))
    
  def update_with(self,datas):
    lat=datas.get_latency()
     
    #aggr evaluate
    if lat is not None and datas.get_bytes()>0 and datas.get_int_code() in [200,]:
      md=ft(lat)
      pos=0
      while pos<len(INTERVALS) and INTERVALS[pos]<md:
        pos+=1

      if pos<len(INTERVALS):
        idx=str(INTERVALS[pos])
        self.counter[idx]=1+self.counter[idx]
      else:
        self.counter['others']=1+self.counter['others']
            
  def print_data(self, printer):
    for threshould in INTERVALS:
      printer(id="numbers%s"%str(threshould).replace('.',''),
              value=self.counter[str(threshould)],
              label="Paged served in less than %s sec during last %s mins"%(threshould,MINUTES,))

    printer(id="numbersother",
            value=self.counter['others'])
