@rem -*- mode: bat; coding: utf-8 -*-
@REM ~ (c) Valik mailto:vasnake@gmail.com
@REM ~ Python tools executor

@echo off
chcp 1251 > nul
set wd=%~dp0
pushd "%wd%"

set PROJECT_DIR=c:\d\code\git\casebook.ru
set path=%path%;c:\d\Python27;c:\d\Python27\Scripts

@REM ~ GOTO createVirtualenv
@REM ~ GOTO installDevelop
@REM ~ GOTO makeSourceDistribution
@REM ~ GOTO createRequirements

GOTO execCasebookReader

@REM ~ ################################################################################

:createVirtualenv
pushd %PROJECT_DIR%
virtualenv  --no-site-packages env
exit

:makeSourceDistribution
pushd %PROJECT_DIR%
call env\scripts\activate.bat
python setup.py sdist
exit

:installDevelop
pushd %PROJECT_DIR%
call env\scripts\activate.bat
python setup.py develop
exit

:createRequirements
pushd %PROJECT_DIR%
call env\scripts\activate.bat
pip freeze > requirements.txt
type requirements.txt
exit

:execCasebookReader
pushd %PROJECT_DIR%
call env\scripts\activate.bat
set CASEBOOK_USER=user name
set CASEBOOK_PASSWORD=secret
set CASEBOOK_DATA=c:\d\code\git\casebook.ru\data
@REM Time in hours to next try to download an existent case/side data
set CASEBOOK_FRESH_PERIOD=12
@REM Time in seconds, stop waiting for a responce after x seconds
set CASEBOOK_REQ_TIMEOUT=60
@REM Recursion limit
set CASEBOOK_RECUR=2
set CASEBOOK_CODEPAGE=UTF-8
set PYTHONIOENCODING=UTF-8
python -u -m casebook
exit

:endOfScript
popd
exit
