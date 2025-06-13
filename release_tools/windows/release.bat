@echo off
echo VARSYS Kitchen Dashboard - Release Manager
echo =========================================
echo.

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help

if "%1"=="current" goto :current
if "%1"=="patch" goto :patch
if "%1"=="minor" goto :minor
if "%1"=="major" goto :major
if "%1"=="set" goto :set
if "%1"=="build" goto :build
if "%1"=="release" goto :release
if "%1"=="full" goto :full

goto :help

:current
echo Getting current version...
python update_version.py current
goto :end

:patch
echo Incrementing patch version...
python update_version.py increment patch
goto :end

:minor
echo Incrementing minor version...
python update_version.py increment minor
goto :end

:major
echo Incrementing major version...
python update_version.py increment major
goto :end

:set
if "%2"=="" (
    echo Error: Version number required
    echo Usage: release.bat set 1.2.0
    goto :end
)
echo Setting version to %2...
python update_version.py set %2
goto :end

:build
echo Building application...
python release_automation.py build
goto :end

:release
if "%2"=="" (
    echo Error: Version number required
    echo Usage: release.bat release 1.2.0
    goto :end
)
echo Preparing release %2...
python update_version.py release %2
goto :end

:full
if "%2"=="" (
    echo Error: Version number required
    echo Usage: release.bat full 1.2.0
    goto :end
)
echo Starting full release process for version %2...
python release_automation.py full %2
goto :end

:help
echo Usage: release.bat [command] [options]
echo.
echo Commands:
echo   current           - Show current version
echo   patch             - Increment patch version (1.0.0 -> 1.0.1)
echo   minor             - Increment minor version (1.0.0 -> 1.1.0)
echo   major             - Increment major version (1.0.0 -> 2.0.0)
echo   set [version]     - Set specific version (e.g., 1.2.0)
echo   build             - Build application only
echo   release [version] - Prepare release with notes
echo   full [version]    - Complete release process
echo   help              - Show this help
echo.
echo Examples:
echo   release.bat current
echo   release.bat patch
echo   release.bat set 1.1.0
echo   release.bat full 1.1.0
echo.

:end
pause
