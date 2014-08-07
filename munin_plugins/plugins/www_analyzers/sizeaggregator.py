from collections import Counter

from math import log


from munin_plugins.plugins.www_analyzers.base import BaseCounter

INTERVALS=(1024, 10240, 102400,1048576,)
COLORS={
  '1024':'00FF00',
  '10240':'88FF00', 
  '102400':'FFFF00',
  '1048576':'FF8800',
}
CODES = [200,]

class SizeAggregator(BaseCounter):
  id='sizeaggregator'
  base_title="Pages by size"
  _defaults={}
  
  def __init__(self,title,group):    
    super(SizeAggregator,self).__init__(title,group)
    self.label="number of pages"
    self.counter=Counter(dict([(str(i),0) for i in INTERVALS]+[('others',0)]))
    
  def update_with(self,datas):
    val=datas.get_bytes()
     
    #aggr evaluate
    if val is not None and datas.get_bytes()>0 and datas.get_int_code() in CODES:
      pos=0
      while pos<len(INTERVALS) and INTERVALS[pos]<int(val):
        pos+=1

      if pos<len(INTERVALS):
        idx=str(INTERVALS[pos])
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
    for threshould in INTERVALS:
      printer(id="numbers%s"%str(threshould).replace('.',''),
              value=self.counter[str(threshould)],
              label='< %s'%self.millify(threshould),
              color=COLORS[str(threshould).replace('.','')],
              draw="AREASTACK")

    printer(id="numbersother",
            value=self.counter['others'],
            label="others",
            color='FF0000',
            draw="AREASTACK")
