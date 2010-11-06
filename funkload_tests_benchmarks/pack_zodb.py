# Pack the main Data.fs
# to run this script you need to stop the zope server and :
#   cat pack_zodb.py | /path/to/zope/bin/zopectl debug
import time
print "\n###\n### Packing main zodb ...\n###"
db = app._p_jar.db()
time_start = time.time()
t = db.pack()
time_stop = time.time()
dt = (time_stop - time_start) / 60.
print "\n###\n### Packing done in %.2f minutes.\n###" % dt
