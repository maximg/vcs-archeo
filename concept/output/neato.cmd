set BIN="C:\Program Files\Graphviz 2.28\bin"

%BIN%\neato -Tcmapx -o%1.map -Tpng -o%1.png %1.dot 
rem start %1.png

