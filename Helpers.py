def bisect_by_attr(a_list,attr,value):
  """
  assumes a_list is sorted by attr
  returns an index at which value can be inserted while maintaining the sort 
  of the list
  always returns the earliest possible index
  """
  if len(a_list) == 0:
    return 0
  if value < getattr(a_list[0],attr):
    return 0
  if value > getattr(a_list[-1],attr):
    return len(a_list)
  lower_ind = 0
  upper_ind = len(a_list)-1
  while True:
    lower_val = getattr(a_list[lower_ind],attr)
    upper_val = getattr(a_list[upper_ind],attr)
    diff = upper_ind - lower_ind
    if diff <= 1:
      if value <= lower_val: return lower_ind
      return upper_ind
    middle_ind = lower_ind + diff/2
    middle_val = getattr(a_list[middle_ind],attr)
    #print "lower: %d middle: %d upper: %d" % (lower_ind,middle_ind,upper_ind)
    if value <= middle_val:
      upper_ind = middle_ind
    else:
      lower_ind = middle_ind

if __name__ == "__main__":
  import random
  nums = []
  for i in range(30):
    x = random.randint(-1000,1000)
    index = bisect_by_attr(nums,'real',x)
    nums.insert(index,x)
  assert (nums == sorted(nums))
  
  class TestClass(object):
    def __init__(self,id,value):
      self.id = id
      self.value = value
  
  def verify(the_list):
    last_val = None
    last_id = None
    for item in the_list:
      if last_id > item.id and last_val <= item.value:
        return False
      val = item.value
      id = item.id
    return True

  this_list = []
  for i in range(100):
    item = TestClass(i,random.randint(0,5))
    this_list.insert(bisect_by_attr(this_list,'value',item.value),item)
  print ["%d %d" % (x.id,x.value) for x in this_list]
  assert verify(this_list)