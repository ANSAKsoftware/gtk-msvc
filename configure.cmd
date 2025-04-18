@echo off
REM ########################################################################
REM
REM Copyright (c) 2025, Arthur N. Klassen
REM All rights reserved.
REM
REM This program is free software; you can redistribute it and/or modify
REM it under the terms of the GNU General Public License as published by
REM the Free Software Foundation; either version 2 of the License, or
REM (at your option) any later version.
REM
REM This program is distributed in the hope that it will be useful,
REM but WITHOUT ANY WARRANTY; without even the implied warranty of
REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM GNU General Public License for more details.
REM
REM You should have received a copy of the GNU General Public License along
REM with this program; if not, write to the Free Software Foundation, Inc.,
REM 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
REM
REM Also, please receive this blessing:
REM
REM    May you do good and not evil.
REM    May you find forgiveness for yourself and forgive others.
REM    May you share freely, never taking more than you give.
REM
REM ###########################################################################
REM
REM configure.cmd -- A Windows .cmd file to call configure.py
REM
REM ###########################################################################
REM determine location if any of python3

if "%1"=="--help" goto help
if "%1"=="-h" goto help

REM find python -- manually? over-ride with that
if "%1"=="--python" goto neither

REM try python to see if it's version 3 (blows up if absent)
python choosep3.py
if not errorlevel 3 goto tryp3
python configure.py python %*
goto done

:tryp3
python3 choosep3.py
if not errorlevel 3 goto noThreeIn3
python3 configure.py python3 %*
goto done

:noThreeIn3
python choosep3.py
echo python selects version %ERRORLEVEL%
python3 choosep3.py
echo python3 selects version %ERRORLEVEL%
echo Have we moved to Python4?
goto done

:neither
shift
if "%1"=="" goto help
%1 configure.py %*
goto done

:help
echo configure.cmd looks for Python 3 and uses it to run configure.py.
echo.
echo Parameters passed to configure.py are
echo    * optionally, --python followed by the command that runs python 3
echo    * all the parameters you might pass in to configure.cmd,
echo          try python3 configure.py --help to see them
echo.
echo What those additinoal parameters might be are explained by running
echo python3 configure.py --help
echo.
echo If you get a 'not recognized' error message about python, you need to
echo install a python3 implementation; at time of writing, one option is:
echo https://www.python.org/downloads/release/python-3102/
echo.
echo If you get a 'not recognized' error message about makensis, you may want
echo to install it. At time of writing, version 3.08 can be acquired from
echo https://nsis.sourceforge.io/Download

:done
