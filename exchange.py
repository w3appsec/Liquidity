class exchange:
  # Exchange Order Format
  initNumIndex = 0  
  currNumIndex = 1  
  priceIndex   = 2  

  def __init__(self, exchangeName):
    self.x = {}
    self.name = exchangeName

  def add(self, sym, numOrig, num, price):
    self.x[sym] = [numOrig, num, price]

  def process(self, A, B, numAin, uid):
    # A = incoming commodity, B = outgoing

    # Unpack Exchange Order
    numAt0 = int(self.x[A][self.initNumIndex])
    numBt0 = int(self.x[B][self.initNumIndex])
    numA   = int(self.x[A][self.currNumIndex])
    numB   = int(self.x[B][self.currNumIndex])
    priceA = int(self.x[A][self.priceIndex])
    priceB = int(self.x[B][self.priceIndex])

    # Core Exchange Algorithm
    k = numAt0 * numBt0
    numAnew = numA + numAin
    numBnew = int(k / numAnew)
    outB    = numB - numBnew
    priceAnew = numAt0 / numAnew
    priceBnew = numBt0 / numBnew

    # Update Exchange
    self.x[A][self.currNumIndex] = numAnew
    self.x[A][self.priceIndex] = priceAnew
    self.x[B][self.currNumIndex] = numBnew
    self.x[B][self.priceIndex] = priceBnew

    # Generate Current Commodity State
    state = {} 
    state["exchangeName"] = self.name 
    state["retNum"] = outB
    state["syms"] = [{A:self.x[A]},{B:self.x[B]}] 
    state["uid"] = uid 

    return(state)

