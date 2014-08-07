from collections import Counter
from munin_plugins.utils import ft

from munin_plugins.plugins.www_analyzers.base import BaseCounter

INTERVALS=(.5,1,2,5)    
COLORS={
  '05':'00FF00',
  '1':'88FF00', 
  '2':'FFFF00',
  '5':'FF8800',
}
CODES = [200,]

class LatencyAggregator(BaseCounter):
  id='latencyaggregator'
  base_title="Pages by latency"
  
  def __init__(self,title,group):    
    super(LatencyAggregator,self).__init__(title,group)
    self.label="number of pages"
    self.counter=Counter(dict([(str(i),0) for i in INTERVALS]+[('others',0)]))
    
  def update_with(self,datas):
    lat=datas.get_float_latency()
     
    #aggr evaluate
    if lat is not None and datas.get_bytes()>0 and datas.get_int_code() in CODES:
      pos=0
      while pos<len(INTERVALS) and INTERVALS[pos]<lat:
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
              label="< %s sec"%threshould,
              color=COLORS[str(threshould).replace('.','')],
              draw="AREASTACK")

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color='FF0000',
            draw="AREASTACK")
