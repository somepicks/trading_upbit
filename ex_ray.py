import time
import datetime
import ray


ray.init()

def do_some_work1(x):
    time.sleep(1) # 1초 지연.
    return x

@ray.remote
def do_some_work2(x):
    time.sleep(1) # 1초 지연.
    return x

@ray.remote
def do_some_work3(x):
    time.sleep(1) # 1초 지연.
    return x

start = datetime.datetime.now()
results = [do_some_work1(x) for x in range(4)]
print("duration =", datetime.datetime.now() - start)
print("results = ", results)

start = datetime.datetime.now()
results = [ray.get(do_some_work2.remote(x)) for x in range(4)]
print("duration =", datetime.datetime.now() - start)
print("results = ", results)

start = datetime.datetime.now()
results = [do_some_work3.remote(x) for x in range(4)]
results = ray.get(results)
print("duration =", datetime.datetime.now() - start)
print("results = ", results)


start = datetime.datetime.now()
value = []
for x in range(4):
    val = do_some_work3.remote(x)
    results = value.append(val)
results = ray.get(results)
print("duration =", datetime.datetime.now() - start)
print("results = ", results)