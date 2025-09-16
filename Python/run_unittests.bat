REM @echo off
 REM Run all unit tests in the current directory and subdirectories
 REM python -m unittest discover -s UnitTests -p "test_*.py"
 REM Alternatively, run a specific test file
 REM python -m unittest UnitTests\test_profisee_common.

REM Has to be run with Python 3.13

py -m unittest -v

