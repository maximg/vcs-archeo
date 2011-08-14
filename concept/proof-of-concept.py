#import re
import sqlite3
import pprint
import pydot
import sys

maxNodes = 300

if len(sys.argv) > 1:
	proj = sys.argv[1]
else:
	proj = 'svnplot'

#proj = 'hadoop-common'
#proj = 'squirrelmail'
#proj = 'squirrel-sql'
#proj = 'notepad-plus'
#proj = 'zero-install'
#proj = 'codeswarm'
	
conn = sqlite3.connect('..\\data\\' + proj + '\\' + proj + '.sqlite')

def getMinMaxChanges():
	c = conn.cursor()
	if proj == 'hadoop-common':
		rows = c.execute('SELECT min(cnt), max(cnt)  as max FROM SvnNodes')
		for row in rows:
			min = row[0]
			max = row[1]
			c.close()
			return (min,max)
	c.close()
	return (1,100)

def getMinMaxLinkWeight():
	c = conn.cursor()
	if proj == 'hadoop-common':
		rows = c.execute('SELECT min(cnt), max(cnt)  as max FROM SvnLinks')
		for row in rows:
			min = row[0]
			max = row[1]
			c.close()
			return (min,max)
	c.close()
	return (1,100)

def getNodes():
	c1 = conn.cursor()
	nodes = []
	rows = c1.execute('''
	SELECT pths.path, changedpathid, count(revno) as cnt FROM SVNLogDetail dt, SVNPaths pths
	where dt.changedpathid = pths.id
	group by changedpathid  
	order by cnt desc''')
	for row in rows:
		if row[1] < maxNodes:
			new_node = (row[1],row[2])
			nodes.append(new_node)
	c1.close()
	return nodes

def getColor(cnt, min, max):
	#pprint.pprint(row)
	if cnt > max/5:
		color = "red"
	elif cnt > max/10:
		color = "yellow"
	else:
		color = "grey"
	return color

(min,max) = getMinMaxChanges()

graph = pydot.Dot(graph_type='graph', overlap='scale')

for node in getNodes():
	graph.add_node(pydot.Node(node[0], style="filled", fillcolor=getColor(node[1], min, max)))

c = conn.cursor()
links = c.execute('''
SELECT t1.changedpathid p1, t2.changedpathid p2, count(t1.revno) weight
from SVNLogDetail t1, SVNLogDetail t2
where t1.revno = t2.revno
and p1 < p2
group by p1,p2
order by  p1, p2, weight''')

def getLength(weight):
	if weight > 1:
		return 0.5
	return 1
	
def getStyle(weight):
	if weight > 1:
		return 'bold'
	return 'invis'
	
for link in links:
	if link[0] < maxNodes and link[1] < maxNodes:
		graph.add_edge( pydot.Edge( link[0], link[1], len=getLength(link[2]), style=getStyle(link[2]) ) )

graph.write(proj + '.dot')
graph.write_png(proj + '.png', prog='neato')

c.close()
conn.close()