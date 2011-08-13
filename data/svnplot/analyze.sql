
-- get list of nodes
SELECT pths.path, changedpathid, count(revno) as cnt FROM SVNLogDetail dt, SVNPaths pths
where dt.changedpathid = pths.id
group by changedpathid  
order by cnt desc

-- get links
SELECT t1.changedpathid p1, t2.changedpathid p2, count(t1.revno) weight
from SVNLogDetail t1, SVNLogDetail t2
where t1.revno = t2.revno
and p1 < p2
group by p1,p2
order by  p1, p2, cnt