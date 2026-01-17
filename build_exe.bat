@echo off
REM Build script for creating a Windows exe using PyInstaller
REM Usage: run this from project root in an Administrator or normal PowerShell/Command prompt

REM 1) Create/activate your virtualenv (optional but recommended)
REM C:\Users\QROBOT\AppData\Local\Python\bin\python.exe -m venv .venv
REM .\.venv\Scripts\activate

echo Installing required Python packages...
pip install --upgrade pip
pip install -r requirements.txt
pip install --upgrade pyinstaller

REM Set the entry script here (change if you want another file)
REM Determine entry script: prefer ytDownload_Qt5.py, fallback to other known filenames
set ENTRY_CANDIDATES=ytDownload_Qt5.py ytDownload_Qt5.py ytDownload.py
set ENTRY=
for %%F in (%ENTRY_CANDIDATES%) do (
    if exist %%F (
        set ENTRY=%%F
        goto :FOUND_ENTRY
    )
)
:FOUND_ENTRY
if "%ENTRY%"=="" (
    echo ERROR: No entry script found. Please set the ENTRY variable in this script to your main .py file.
    pause
    exit /b 1
)
echo Using entry script: %ENTRY%
set NAME=ytdownload_gui

REM Optional: include an icon file if you have one (download.ico)
set ICON=download.ico

REM Optional: include extra files (eg. download.png). Format for Windows: "src;dest"
set ADD_DATA=download.png;.

echo Running PyInstaller using "python -m PyInstaller" to avoid Scripts PATH issues...
REM Try to detect _ctypes.pyd and libffi DLLs in the active Python and include them as binaries
set ADD_BINARY_ARGS=
for /f "delims=" %%P in ('python -c "import _ctypes,sys; print(getattr(_ctypes,'__file__',''''))"') do set CTYPES_PYD=%%P
if defined CTYPES_PYD (
    echo Found _ctypes: %CTYPES_PYD%
    set ADD_BINARY_ARGS=--add-binary "%CTYPES_PYD%;."
) else (
    echo Warning: _ctypes not found in current Python environment.
)

for /f "delims=" %%L in ('python -c "import sys,os,glob; p=os.path.join(sys.base_prefix,'DLLs'); l=glob.glob(os.path.join(p,'libffi*.dll')); print(l[0] if l else '')"') do set LIBFFI_DLL=%%L
if defined LIBFFI_DLL (
    echo Found libffi DLL: %LIBFFI_DLL%
    if defined ADD_BINARY_ARGS (
        set ADD_BINARY_ARGS=%ADD_BINARY_ARGS% --add-binary "%LIBFFI_DLL%;."
    ) else (
        set ADD_BINARY_ARGS=--add-binary "%LIBFFI_DLL%;."
    )
) else (
    echo Warning: libffi DLL not found in Python DLLs directory.
)

echo Binary args: %ADD_BINARY_ARGS%

if exist %ICON% (
    python -m PyInstaller --noconfirm --windowed --name %NAME% --icon %ICON%  --add-data "%ADD_DATA%" %ADD_BINARY_ARGS% %ENTRY%
) else (
    python -m PyInstaller --noconfirm --windowed --name %NAME%  --add-data   "%ADD_DATA%" %ADD_BINARY_ARGS% %ENTRY%
)

echo Build finished. Dist folder contains the exe: dist\%NAME%.exe
pause