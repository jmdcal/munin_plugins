from collections import Counter

from math import log

from ..utils import ft
from ..env import SIZE_INTERVALS
from ..env import MINUTES
from ..env import SIZE_COLORS
from ..env import SIZE_CODES

from .base import BaseCounter

class SizeAggregator(BaseCounter):
  id='sizeaggregator'
  base_title="Bytes downloaded"
  
  def __init__(self,title,group):    
    super(SizeAggregator,self).__init__(title,group)
    self.label="number of pages in %s mins" %MINUTES
    self.counter=Counter(dict([(str(i),0) for i in SIZE_INTERVALS]+[('others',0)]))
    
  def update_with(self,datas):
    val=datas.get_bytes()
     
    #aggr evaluate
    if val is not None and datas.get_bytes()>0 and datas.get_int_code() in SIZE_CODES:
      pos=0
      while pos<len(SIZE_INTERVALS) and SIZE_INTERVALS[pos]<int(val):
        pos+=1

      if pos<len(SIZE_INTERVALS):
        idx=str(SIZE_INTERVALS[pos])
        self.counter[idx]=1+self.counter[idx]
      else:
        self.counter['others']=1+self.counter['others']
            
  def millify(self,value):
    byteunits = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    try:
        exponent = int(log(value, 1024))
        res="%.1f %s" % (float(value) / pow(1024, exponent), byteunits[exponent])
    except:
        res="0B"
    return res
            
  def print_data(self, printer, w=None,c=None):
    for threshould in SIZE_INTERVALS:
      printer(id="numbers%s"%str(threshould).replace('.',''),
              value=self.counter[str(threshould)],
              label='< %s'%self.millify(threshould),
              color=SIZE_COLORS[str(threshould).replace('.','')],
              draw="AREASTACK")

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color='FF0000',
            draw="AREASTACK")
