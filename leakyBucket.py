import asyncio
import datetime
import threading
import queue


class Bucket(object):
    def __init__(self, qps, max_size):
        self.interval = datetime.timedelta(seconds=1.0 / qps)
        self.queue = queue.Queue(max_size)
        self.lock = threading.Lock()
        self.last = datetime.datetime.min

    def empty(self):
        self.lock.acquire()
        try:
            return self.queue.empty()
        finally:
            self.lock.release()

    def put(self, value):
        if self.queue.full():
            return False
        with self.lock:
            self.queue.put(value)

    async def take(self):
        while not self.empty():
            duration = datetime.datetime.now() - self.last
            if duration <= self.interval:
                remain = self.interval - duration
                await asyncio.sleep(remain.microseconds / 1000000.0)
            self.last = datetime.datetime.now()
            with self.lock:
                value = self.queue.get()
            yield value


async def take(bucket):
    async for i in b.take():
        print("{0}: {1}".format(datetime.datetime.now(), i))

b = Bucket(10, 20)
for i in range(100):
    b.put(i)

loop = asyncio.get_event_loop()
loop.run_until_complete(take(b))
loop.close()
