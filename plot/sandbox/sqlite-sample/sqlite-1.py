#import re
import sqlite3
import pprint


# Create a connection to the database.
conn = sqlite3.connect('..\\..\\..\\svnplot\\svnplot.sqlite')

# Create a cursor object to do the interacting.
c = conn.cursor()

# Grab the columns with the time-zoned dates.
old_rows = c.execute('''
SELECT t1.changedpathid p1, t2.changedpathid p2, count(t1.revno) weight
from SVNLogDetail t1, SVNLogDetail t2
where t1.revno = t2.revno
and p1 < p2
group by p1,p2
order by  p1, p2, weight''')

# Create an empty list that will hold the new tuples.
new_rows = []

# Iterate over the result, tearing out the time zone as we go.
for row in old_rows:
    id1 = row[0]
    id2 = row[1]
    weight = row[2]
    new_row = (id1, id2, weight)# Here is the new tuple ...
    new_rows.append(new_row)# ... appended to our list.

#pprint(new_rows)	
# Iterate through the new list of tuples and put them in the database.
for row in new_rows:
    #c.execute('UPDATE objects SET created=?,modified=? WHERE id=?',        (row[0:3]))
	pprint.pprint(row)

# Commit the changes and close everything.
#conn.commit()
c.close()
conn.close()