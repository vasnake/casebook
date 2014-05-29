@rem -*- mode: bat; coding: utf-8 -*-
@REM ~ (c) Valik mailto:vasnake@gmail.com
@REM ~ Python tools executor

REM ~ 1. Install Python 2.7.
REM ~ 2. set envvars PROJECT_DIR, path and others under label 'execCasebookReader'.
REM ~ 3. Create file %CASEBOOK_DATA%\input.lst and fill it with your queries, like '№ А65-27211/2011'.
REM ~ 4. Execute once each step in turn: installVirtualenvLib, createVirtualenv, installDevelop.
REM ~ 5. Now you can run step execCasebookReader as many times as you wish.

@echo off
chcp 1251 > nul
set wd=%~dp0
pushd "%wd%"

set PROJECT_DIR=C:\Users\valik\Downloads\casebook-dev\casebook-dev
set path=%path%;C:\Python27;C:\Python27\Scripts
@REM SET http_proxy=http://user:password@someproxy.com:3128

@REM ~ GOTO installVirtualenvLib
@REM ~ GOTO createVirtualenv
@REM ~ GOTO installDevelop

@REM ~ GOTO execCasebookReader

@REM ~ ################################################################################

@REM ~ GOTO makeSourceDistribution
@REM ~ GOTO createRequirements

GOTO endOfScript

@REM ~ ################################################################################

:installVirtualenvLib
pushd %PROJECT_DIR%
python -c "from urllib import urlretrieve; urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"
python -u get-pip.py
pip install virtualenv
pause
exit

:createVirtualenv
pushd %PROJECT_DIR%
virtualenv  --no-site-packages env
pause
exit

:makeSourceDistribution
pushd %PROJECT_DIR%
call env\scripts\activate.bat
python setup.py sdist
pause
exit

:installDevelop
pushd %PROJECT_DIR%
call env\scripts\activate.bat
python setup.py develop
pause
exit

:createRequirements
pushd %PROJECT_DIR%
call env\scripts\activate.bat
pip freeze > requirements.txt
type requirements.txt
pause
exit

:execCasebookReader
pushd %PROJECT_DIR%
call env\scripts\activate.bat
set CASEBOOK_USER=username
set CASEBOOK_PASSWORD=secret
set CASEBOOK_DATA=C:\Users\valik\Downloads\t
@REM Time in hours to next try to download an existent case/side data
set CASEBOOK_FRESH_PERIOD=12
@REM Time in seconds, stop waiting for a responce after x seconds
set CASEBOOK_REQ_TIMEOUT=60
@REM Recursion limit
set CASEBOOK_RECUR=2
@REM https://docs.python.org/2/using/cmdline.html#envvar-PYTHONIOENCODING
set PYTHONIOENCODING=cp1251:backslashreplace
python -u -m casebook
pause
exit

:endOfScript
popd
pause
exit
