@echo off
rem Get data for the project
rem Usage: svnplot-get.cmd svn_url proj_name

set SVNLOG=d:\bin\Python27\Lib\site-packages\svnplot\svnlog2sqlite.py
set SVN=%1
set PROJ=%2

if x%PROJ% == x (
	echo Usage: svnplot-get svn_url proj_name
	exit /B
)

if not exist %PROJ% mkdir %PROJ%

python %SVNLOG% -v -l  %SVN% %PROJ%\%PROJ%.sqlite >%PROJ%\svnplot-get.log

pause
