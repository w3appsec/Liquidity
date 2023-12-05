from exchange import exchange 
from threading import Thread, Condition
from collections import deque, defaultdict 
from random import random, seed
from datetime import datetime
import time  

# Coin Symbols
cm1 = "VER"
cm2 = "ZYC"

# Crypto Exchanges
ex1 = "CBA"
ex2 = "KRK"

exchangeQ    = deque()     # Exchange Queue 
exchangeLock = Condition() # Exchange Semaphore 
analyzerQ    = deque()     # Analyzer Queue
analyzerLock = Condition() # Analyzer Semaphore

# For Random User UID, PRNG is OK
ts = datetime.today().timestamp()
seed(int(ts))
marketMakerUid = int(10000)

class OrderGenerator(Thread):
  def run(self):
    global exchangeQ 
    global marketMakerUid 
    numUsers     = marketMakerUid - 1 
    orderSizeMax = 1000
    ordersPerSec = 10 
    while True:
      u1 = int(random()*numUsers)
      u2 = int(random()*numUsers)
      orderSize1 = int((random()*orderSizeMax)+1)
      orderSize2 = int((random()*orderSizeMax)+1)
      order1 = f'{cm1} {cm2} {orderSize1} {ex1} {u1}'
      order2 = f'{cm2} {cm1} {orderSize2} {ex2} {u2}'
      print ("\n\n--------------------------\n"+str(datetime.today()))
      print("Customer Orders:")
      print(order1+"(Uid)")
      print(order2+"(Uid)")
      with exchangeLock:
        exchangeQ.append(order1)
        exchangeQ.append(order2)
        exchangeLock.notify() 
      time.sleep(1 / ordersPerSec)

class ExchangeAnalyzer(Thread):
  global marketMakerUid
  def run(self):
    global analyzerQ 
    cx = defaultdict(lambda: defaultdict(dict))
    while True:
      with analyzerLock:
        analyzerLock.wait_for(lambda: len(analyzerQ) > 0)
        exchState = analyzerQ.popleft()
        exchName = exchState["exchangeName"]
        uid = int(exchState["uid"])

        for i in range(0, 2): # num of exchngs
          for sym, param in exchState["syms"][i].items():
            cx[sym][exchName]['Bid'] = 0.99*param[2]
            cx[sym][exchName]['Ask'] = 1.01*param[2]
            cx[sym][exchName]['deltaN'] = int(param[1]-param[0])
        self.display(dict(cx))
        if uid != marketMakerUid:
          self.marketMaker(dict(cx))

  def marketMaker(self, exchangeObjs):
    xo = exchangeObjs 
    if (xo.get(cm1) != None) and (xo[cm1].get(ex1) != None):
      cm1ex1D = xo[cm1][ex1]['deltaN']
    if (xo.get(cm1) != None) and (xo[cm1].get(ex2) != None):
      cm1ex2D = xo[cm1][ex2]['deltaN']
    if (xo.get(cm2) != None) and (xo[cm2].get(ex1) != None):
      cm2ex1D = xo[cm2][ex1]['deltaN']
    if (xo.get(cm2) != None) and (xo[cm2].get(ex2) != None):
      cm2ex2D = xo[cm2][ex2]['deltaN']

    if (xo.get(cm1) != None) and (xo[cm1].get(ex1) != None) and (xo[cm1].get(ex2) != None):
      if (cm1ex1D > 0) and (cm1ex2D < 0):
        order1 = f'{cm2} {cm1} {-cm2ex1D} {ex1} {marketMakerUid}'
        print("Market Maker Order: "+order1+"(Uid)")
        order2 = f'{cm1} {cm2} {-cm1ex2D} {ex2} {marketMakerUid}'
        print("Market Maker Order: "+order2+"(Uid)")
        with exchangeLock:
          exchangeQ.append(order1)
          exchangeQ.append(order2)
          exchangeLock.notify() 

    if (xo.get(cm2) != None) and (xo[cm2].get(ex1) != None) and (xo[cm2].get(ex2) != None):
      if (cm2ex1D > 0) and (cm2ex2D < 0):
        order1 = f'{cm2} {cm1} {cm2ex1D} {ex1} {self.marketMakerUid}'
        print("Market Maker Order: "+order1)
        order2 = f'{cm1} {cm2} {cm1ex2D} {ex2} {self.marketMakerUid}'
        print("Market Maker Order: "+order2)
        with exchangeLock:
          exchangeQ.append(order1)
          exchangeQ.append(order2)
          exchangeLock.notify() 

  def display(self, exchangeObjs): 
    xo = exchangeObjs 
    if xo.get(cm1) != None:
      print("\nMARKET INFO:")
      if xo[cm1].get(ex1) != None:
        print(f"{cm1} {ex1} Bid: {xo[cm1][ex1]['Bid']:.2f}")
        print(f"{cm1} {ex1} Ask: {xo[cm1][ex1]['Ask']:.2f}")
        print(f"{cm1} {ex1} deltaN: {xo[cm1][ex1]['deltaN']}")
      if xo[cm1].get(ex2) != None:
        print(f"{cm1} {ex2} Bid: {xo[cm1][ex2]['Bid']:.2f}")
        print(f"{cm1} {ex2} Ask: {xo[cm1][ex2]['Ask']:.2f}")
        print(f"{cm1} {ex2} deltaN: {xo[cm1][ex2]['deltaN']}")
    if xo.get(cm2) != None:
      if xo[cm2].get(ex1) != None:
        print(f"{cm2} {ex1} Bid: {xo[cm2][ex1]['Bid']:.2f}")
        print(f"{cm2} {ex1} Ask: {xo[cm2][ex1]['Ask']:.2f}")
        print(f"{cm2} {ex1} deltaN: {xo[cm2][ex1]['deltaN']}")
      if xo[cm2].get(ex2) != None:
        print(f"{cm2} {ex2} Bid: {xo[cm2][ex2]['Bid']:.2f}")
        print(f"{cm2} {ex2} Ask: {xo[cm2][ex2]['Ask']:.2f}")
        print(f"{cm2} {ex2} deltaN: {xo[cm2][ex2]['deltaN']}")

class ExchangeController(Thread):
  xchs = {}
  xchs[ex1] = exchange(ex1)
  xchs[ex2] = exchange(ex2)

  def run(self):
    global exchangeQ 
    pool = 500000
    for sym, xch in self.xchs.items():
      self.xchs[sym].add(f"{cm1}", pool, pool, 1)
      self.xchs[sym].add(f"{cm2}", pool, pool, 1)
    while True:
      with exchangeLock:
        exchangeLock.wait_for(lambda: len(exchangeQ) > 0)
        order = exchangeQ.popleft()

      # Unpack the order
      params = order.split()
      symIn  = params[0]
      symOut = params[1]
      numIn  = int(params[2])
      exchng = params[3]
      uid    = params[4]

      # Activate the Exchange
      state  = self.xchs[exchng].process(symIn, symOut, numIn, uid)

      # Analyze the new Exchange state
      with analyzerLock:
        analyzerQ.append(state)
        analyzerLock.notify() 

# Start All Processes
ExchangeController().start()
ExchangeAnalyzer().start()
OrderGenerator().start()


