#import re
import sqlite3
import pprint
import pydot
import sys

nodes = {}
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

def getNodes():
	c1 = conn.cursor()
	rows = c1.execute('''
	select nd.id, nd.path, nd.rank, cp.fromId parent from SVNNodesVw nd 
	left outer join SVNCopiesVw cp on nd.id = cp.id
	order by nd.id''')
	for node in rows:
		id = node[0]
		if id < maxNodes:
			nodes[id] = node
	c1.close()

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

remap = {}

getNodes()
new_nodes = {}

for id in nodes:
	(x, path, rank, parent) = nodes[id]
	# check for renames
	if not parent is None:
		pprint.pprint(nodes[parent])
		(x1, path1, prank, parent1) = nodes[parent]
		rank = rank + prank
		remap[parent] = id
		del new_nodes[parent]
	new_nodes[id] = (id, path, rank, parent)
	#pprint.pprint(new_nodes[id])

for id in new_nodes:
	(x, path, rank, parent) = new_nodes[id]
	if rank > max/10:
		label = path.split('/')[-1]
	else:
		label = id
	label = path.split('/')[-1]
	color = getColor(rank, min, max)
	shape = "ellipse"
	if label == '':
		# it is a folder
		color = "green"
		label = path.split('/')[-2]
		shape = "box"
	label = label + " (" + str(id) + ")"
	graph.add_node(pydot.Node(id, label=label, style="filled", fillcolor=color, shape=shape, URL=path))

c = conn.cursor()
links = c.execute('''
SELECT t1.changedpathid p1, t2.changedpathid p2, count(t1.revno) weight
from SVNLogDetail t1, SVNLogDetail t2
where t1.revno = t2.revno
and p1 < p2
group by p1,p2
order by  p1, p2, weight''')

def getLength(rank):
	if rank > 1:
		return 0.5
	return 1
	
def getStyle(weight):
	if weight > 1:
		return 'bold'
	return 'invis'
	
def getNode(id):
	while id in remap:
		id = remap[id]
	return id
	
for (id1, id2, linkRank) in links:
	if id1 < maxNodes and id2 < maxNodes:
		#graph.add_edge( pydot.Edge( node1, node2, len=getLength(linkRank), style=getStyle(linkRank) ) )
		node1 = getNode(id1)
		node2 = getNode(id2)
		graph.add_edge( pydot.Edge( node1, node2, style=getStyle(linkRank), len=0.1 ) )

graph.write(proj + '.dot')
graph.write_png(proj + '.png', prog='neato')
graph.write_cmapx(proj + '.map', prog='neato')

c.close()
conn.close()