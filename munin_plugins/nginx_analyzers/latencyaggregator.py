from collections import Counter
from munin_plugins.utils import ft
from munin_plugins.etc.env import INTERVALS
from munin_plugins.etc.env import MINUTES
from munin_plugins.etc.env import COLORS

from base import BaseCounter

class LatencyAggregator(BaseCounter):
  id='latencyaggregator'
  base_title="Nginx latency"
  
  def __init__(self,title,group):    
    super(LatencyAggregator,self).__init__(title,group)
    self.label="number of pages in %s mins" %MINUTES
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
            
  def print_data(self, printer, w=None,c=None):
    for threshould in INTERVALS:
      printer(id="numbers%s"%str(threshould).replace('.',''),
              value=self.counter[str(threshould)],
              label="%s sec"%threshould,
              color=COLORS[str(threshould).replace('.','')],
              draw="AREASTACK")

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color='FF0000',
            draw="AREASTACK")
