casebook
========

**Casebook** is a Python package for data extraction from the web site casebook.ru

This package can help you to find and download data (in JSON format) from http://casebook.ru/

Usage
-----

Download and unpack package files.

Edit runner script and set variables:

    * PROJECT_DIR
    * CASEBOOK_USER
    * CASEBOOK_PASSWORD
    * CASEBOOK_DATA

PROJECT_DIR is a filesystem folder where package has been unpacked.
CASEBOOK_USER and CASEBOOK_PASSWORD is a login parameters for casebook.ru.
CASEBOOK_DATA is a filesystem folder for store downloaded data.

Install package using virtualenv. You can use runner script for that and,
in that case, run steps createVirtualenv, installDevelop sequentially.

Create text file ${CASEBOOK_DATA}/input.lst
Each line in that file is a query string for searching cases or sides on casebook.ru.

Run the package using runner script, step execCasebookReader.

Wait for a while, get your data from ${CASEBOOK_DATA} folder.
