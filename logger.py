#!/usr/bin/env python3

import redis, os
import datetime, time

db = redis.Redis(host="raspberry.local", port=6379, db=0)

def do_stats():
    l = []
    for k in db.smembers("set:rolling"):
        k = k.decode("utf-8")
        first_dt = db.hget(k, "first_seen").decode("utf-8")
        last_dt = db.hget(k, "last_seen").decode("utf-8")
        ct = int(db.hget(k, "seen_counter"))

        l.append((datetime.datetime.strptime(first_dt, "%d.%m.%Y %H:%M:%S"), k, ct, datetime.datetime.strptime(last_dt, "%d.%m.%Y %H:%M:%S")))

    l.sort()

    t = ""
    for e in l:
        t = "{}\n[{} --> {}] {} {}".format(
            t,
            e[0].strftime("%H:%M:%S"),
            e[3].strftime("%H:%M:%S"),
            e[1],
            e[2])
    return t

while True:
    t = do_stats()
    os.system("clear")
    print(t)
    time.sleep(0.9)
