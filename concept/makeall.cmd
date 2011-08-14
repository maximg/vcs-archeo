
setlocal enabledelayedexpansion

pushd ..\data
for /D %%d in (*.*) do if exist %%d\%%d.sqlite (
	python ..\concept\proof-of-concept.py %%d
	move %%d.dot ..\concept
	move %%d.png ..\concept
	start ..\concept\%%d.png
)
