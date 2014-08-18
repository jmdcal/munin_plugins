from collections import Counter

from munin_plugins.plugins.www_analyzers.base import BaseCounter

class SizeAggregator(BaseCounter):
  id='sizeaggregator'
  base_title="Pages by size"
  _defaults={
    'graph':'AREASTACK',
    'codes':'200',
    'intervals':'1024, 10240, 102400,1048576',
    'color_1024':'00FF00',
    'color_10240':'88FF00', 
    'color_102400':'FFFF00',
    'color_1048576':'FF8800',    
    'color_others':'FF0000',
  }
  
  def __init__(self,title,group):    
    super(SizeAggregator,self).__init__(title,group)
    self.label="number of pages"
    self.counter=Counter(dict([(str(i),0) for i in self.getenv('intervals')]+[('others',0)]))
    
  def update_with(self,datas):
    val=datas.get_bytes()
    intervals=self.getenv('intervals')
    codes=str(self.getenv('codes')).split(',')
    #aggr evaluate
    if val is not None and datas.get_bytes()>0 and datas.get_int_code() in codes:
      pos=0
      while pos<len(intervals) and intervals[pos]<int(val):
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
              label='< %s'%self.millify(threshould),
              color=self.getenv('color_%s'%threshould),
              draw=self.getenv('graph'))

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color=self.getenv('color_others'),
            draw=self.getenv('graph'))
