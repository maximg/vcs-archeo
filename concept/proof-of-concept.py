#import re
import sqlite3
import pprint
import pydot

graph = pydot.Dot(graph_type='graph')

# Create a connection to the database.
conn = sqlite3.connect('..\\data\\svnplot\\svnplot.sqlite')

c1 = conn.cursor()

nodes = c1.execute('''
SELECT pths.path, changedpathid, count(revno) as cnt FROM SVNLogDetail dt, SVNPaths pths
where dt.changedpathid = pths.id
group by changedpathid  
order by cnt desc''')

for node in nodes:
	#pprint.pprint(row)
	if node[2] > 20:
		color = "red"
	elif node[2] > 10:
		color = "yellow"
	else:
		color = "grey"
	graph.add_node(pydot.Node(node[1], style="filled", fillcolor=color))

c1.close()

# Create a cursor object to do the interacting.
c = conn.cursor()

# Grab the links
links = c.execute('''
SELECT t1.changedpathid p1, t2.changedpathid p2, count(t1.revno) weight
from SVNLogDetail t1, SVNLogDetail t2
where t1.revno = t2.revno
and p1 < p2
group by p1,p2
order by  p1, p2, weight''')

#pprint(new_rows)	
# Iterate through the new list of tuples and put them in the database.
for link in links:
	#pprint.pprint(row)
	graph.add_edge(pydot.Edge(link[0],link[1]))

graph.write_png('svnhist.png', prog='neato')

# Commit the changes and close everything.
#conn.commit()
c.close()
conn.close()