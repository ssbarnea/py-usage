"""
Requirements:
* be able to keep Car, Trunk and Engine in separate files
* Trunk and Engine need a car object in order to be initialied (they need to interact in certain cases)
* have engine and tank objects initialized 

car.py
engine.py
tank.py
"""

class Trunk(object):
    def __init__(self, car):
        self._car = car
    def fillUp(self):
        print "taked fillup"

class Engine(object):
    def __init__(self, car):
        self._car = car
    def start(self):
        print "car started"

class Car(object):
    def __init__(self):
        self.trunk = Trunk(self)
        self.engine = Engine(self)

car = Car()
car.trunk.fillUp()
car.engine.start()

print car, car.__dict__

# now we try to upgrade the engine class
