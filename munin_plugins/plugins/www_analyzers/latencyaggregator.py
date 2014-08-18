from collections import Counter

from munin_plugins.plugins.www_analyzers.base import BaseCounter

class LatencyAggregator(BaseCounter):
  id='latencyaggregator'
  base_title="Pages by latency"
  _defaults={
    'graph':'AREASTACK',
    'codes':'200',
    'intervals':'0.5, 1, 2,5',
    'color_05':'00FF00',
    'color_1':'88FF00', 
    'color_2':'FFFF00',
    'color_5':'FF8800',    
  }
  
  def __init__(self,title,group):    
    super(LatencyAggregator,self).__init__(title,group)
    self.label="number of pages"
    self.counter=Counter(dict([(str(i),0) for i in self.getenv('intervals')]+[('others',0)]))
    
  def update_with(self,datas):
    lat=datas.get_float_latency()
    intervals=self.getenv('intervals')
    codes=str(self.getenv('codes')).split(',')
    #aggr evaluate
    if lat is not None and datas.get_bytes()>0 and datas.get_int_code() in codes:
      pos=0
      while pos<len(intervals) and intervals[pos]<lat:
        pos+=1

      if pos<len(intervals):
        idx=str(intervals[pos])
        self.counter[idx]=1+self.counter[idx]
      else:
        self.counter['others']=1+self.counter['others']
            
  def print_data(self, printer, w=None,c=None):    
    for threshould in self.getenv('intervals'):
      printer(id="numbers%s"%str(threshould).replace('.',''),
              value=self.counter[str(threshould)],
              label="< %s sec"%threshould,
              color=self.getenv('color_%s'%str(threshould).replace('.','')),
              draw=self.getenv('graph'))

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color='FF0000',
            draw=self.getenv('graph'))
