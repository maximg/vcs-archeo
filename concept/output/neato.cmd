set BIN="C:\Program Files\Graphviz 2.28\bin"

%BIN%\neato -Tpng svnplot.debug.dot -o svnplot.png
start svnplot.png

