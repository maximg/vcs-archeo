'''
plot.py
Copyright (C) 2011 Maxim Golov maxim.golov@gmail.com

Vuoksa Consulting proprietary
Partially based on SVNPlot (http://code.google.com/p/svnplot) 
--------------------------------------------------------------------------------------
'''
from __future__ import with_statement

__revision__ = '$Revision:$'
__date__     = '$Date:$'

import matplotlib
matplotlib.use('Agg') #Default use Agg backend we don't need any interactive display

import matplotlib.pyplot as plt
import matplotlib.mpl as mpl

from optparse import OptionParser
import sqlite3
import os.path, sys
import string,StringIO
import math
from subprocess import call

from svnplotmatplotlib import *
from svnstats import *

HTMLIndexTemplate ='''
<html>
<head><title>Subversion Stats Plot for $RepoName</title>
    <style type="text/css">
    th {background-color: #F5F5F5; text-align:center}
    /*td {background-color: #FFFFF0}*/
    h3 {background-color: transparent;margin:2}
    h4 {background-color: transparent;margin:1}    
    </style>
</head>
<body>
<table align="center" frame="box">
<caption></caption>
<tr>
    <td align="center" ><h4>Commit Activity By Day of Week </h4><br/>
    <a href="$plot1"><img src="$plot1"></a>
    </td>  
</tr>

</table>
</body>
</html>
'''

HTMLBasicStatsTmpl = '''
'''


GraphNameDict = dict(plot1="plot1")
                         
class SVNPlot(SVNPlotMatplotLib):
    def __init__(self, svnstats, dpi=100, format='png',template=None):
        SVNPlotMatplotLib.__init__(self, svnstats, dpi,format)
        self.commitGraphHtPerAuthor = 2 #In inches
        self.authorsToDisplay = 10
        self.fileTypesToDisplay = 20
        self.dirdepth = 2
        self.setTemplate(template)
        
    def setTemplate(self, template):
        self.template = HTMLIndexTemplate
        if( template != None):
            with open(template, "r") as f:
                self.template = f.read()
 
                
    def AllGraphs(self, dirpath, svnsearchpath='/', thumbsize=100, maxdircount = 10):
        self.svnstats.SetSearchPath(svnsearchpath)

        self.Plot1(self._getGraphFileName(dirpath, "plot1"))

        graphParamDict = self._getGraphParamDict( thumbsize)
        
        htmlidxTmpl = string.Template(self.template)
        htmlidxname = os.path.join(dirpath, "index.htm")
        outstr = htmlidxTmpl.safe_substitute(graphParamDict)
        htmlfile = file(htmlidxname, "w")
        htmlfile.write(outstr.encode('utf-8'))
        htmlfile.close()
                               
    def Plot1(self, filename, months=3):
        self._printProgress("Calculating plot1")
        
        data, labels = self.svnstats.getActivityByWeekday()
        
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        
        ax1 = self._drawBarGraph(data, None,0.5, axes=ax1,color='b')
        ax1.set_ylabel('Commits')
        ax1.set_title('Activity By Day of Week (All time)')

        #fig.savefig(filename, dpi=self.dpi, format=self.format) 

        call(["C:\\Program Files\\Graphviz 2.28\\bin\\neato", "-Tpng","sample.dot","-o","svnplot\\plot1.png"])

    def _getGraphFileName(self, dirpath, graphname):
        filename = os.path.join(dirpath, GraphNameDict[graphname])
        #now add the extension based on the format
        filename = "%s.%s" % (filename, self.format)
        return(filename)
    
    def _getGraphParamDict(self, thumbsize):
        graphParamDict = dict()
        for graphname in GraphNameDict.keys():
            graphParamDict[graphname] = self._getGraphFileName(".", graphname)
            
        graphParamDict["thumbwid"]=str(thumbsize)
        graphParamDict["thumbht"]=str(thumbsize)
        graphParamDict["RepoName"]=self.reponame
        graphParamDict["TagCloud"] = self.TagCloud()
        graphParamDict["AuthCloud"] = self.AuthorCloud()
        graphParamDict["BasicStats"] = self.BasicStats(HTMLBasicStatsTmpl)
        graphParamDict["ActiveFiles"] = self.ActiveFiles()
        graphParamDict["ActiveAuthors"] = self.ActiveAuthors()
            
        return(graphParamDict)


def RunMain():
    usage = "usage: %prog [options] <svnsqlitedbpath> <graphdir>"
    parser = OptionParser(usage)

    parser.add_option("-n", "--name", dest="reponame",
                      help="repository name")
    parser.add_option("-s","--search", dest="searchpath", default="/",
                      help="search path in the repository (e.g. /trunk)")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="display verbose progress")
    parser.add_option("-r", "--dpi", dest="dpi", default=100, type="int",
                      help="set the dpi of output png images")
    parser.add_option("-t", "--thumbsize", dest="thumbsize", default=100, type="int",
                      help="set the width and heigth of thumbnail display (pixels)")    
    parser.add_option("-p", "--template", dest="template", default=None,
                      action="store", type="string", help="template filename (optional)")
    parser.add_option("-m","--maxdir",dest="maxdircount", default=10, type="int",
                      help="limit the number of directories on the graph to the x largest directories")
    
    (options, args) = parser.parse_args()
    
    if( len(args) < 2):
        print "Invalid number of arguments. Use plot.py --help to see the details."
    else:        
        svndbpath = args[0]
        graphdir  = args[1]
        
        if( options.searchpath.endswith('%') == False):
            options.searchpath +='%'
            
        if( options.verbose == True):
            print "Calculating subversion stat graphs"
            print "Subversion log database : %s" % svndbpath
            print "Graphs will generated in : %s" % graphdir
            print "Repository Name : %s" % options.reponame
            print "Search path inside repository : %s" % options.searchpath
            print "Graph thumbnail size : %s" % options.thumbsize
            print "Maximum dir count: %d" % options.maxdircount
            if( options.template== None):
                print "using default html template"
            else:
                print "using template : %s" % options.template
                
        svnstats = SVNStats(svndbpath)     
        svnplot = SVNPlot(svnstats, dpi=options.dpi, template=options.template)
        svnplot.SetVerbose(options.verbose)
        svnplot.SetRepoName(options.reponame)
        svnplot.AllGraphs(graphdir, options.searchpath, options.thumbsize, options.maxdircount)
        
if(__name__ == "__main__"):
    RunMain()
    
