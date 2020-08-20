import threading
import time

counter = 0

def raise_error():
    if counter%2 == 1:
        print("*********entered the raise_error if")
        raise Exception

def printit(timer):
    t = threading.Timer(timer, raise_error())
    t.start()
    time.sleep(3)
    print("*********timer was "+ timer)
        

try:
    print(printit(5))
except:
    print("*********entered exception")
try:
    print(printit(1))
except:
    print("*********entered exception")