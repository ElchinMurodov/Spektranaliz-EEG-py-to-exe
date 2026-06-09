@echo off
REM ===========================================================================
REM  Spektranaliz EEG - avtomatik .exe yig'uvchi skript (Windows)
REM  Mualliflik: Murodov Elchin O'ktamovich
REM
REM  Bu skript:
REM    1) Python virtual muhitini (venv) yaratadi
REM    2) Kerakli kutubxonalarni o'rnatadi (requirements.txt)
REM    3) SVG ikona/logolardan raster (.ico/.png) yasaydi (make_assets.py)
REM    4) PyInstaller orqali .exe yig'adi (spektranaliz_eeg.spec)
REM    5) Inno Setup bo'lsa, o'rnatuvchi (setup.exe) ni ham yasaydi
REM
REM  Ishga tushirish: shu faylni ikki marta bosing yoki cmd da: build.bat
REM ===========================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   Spektranaliz EEG - .exe yig'ish jarayoni boshlandi
echo ============================================================
echo.

REM --- 1. Python mavjudligini tekshirish ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi. https://www.python.org dan Python 3.10+ o'rnating
    echo        va o'rnatishda "Add Python to PATH" belgilang.
    pause
    exit /b 1
)

REM --- 2. Virtual muhit yaratish ---
if not exist ".venv" (
    echo [1/5] Virtual muhit yaratilmoqda...
    python -m venv .venv
) else (
    echo [1/5] Virtual muhit allaqachon mavjud.
)
call ".venv\Scripts\activate.bat"

REM --- 3. Kutubxonalarni o'rnatish ---
echo [2/5] Kutubxonalar o'rnatilmoqda...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [XATO] Kutubxonalarni o'rnatib bo'lmadi. Internet aloqasini tekshiring.
    pause
    exit /b 1
)

REM --- 4. Ikonka va logo rasterlarini yasash ---
echo [3/5] Ikonka (.ico) va logo (.png) rasterlari yasalmoqda...
python make_assets.py
if errorlevel 1 (
    echo [OGOHLANTIRISH] Rasterlar yasalmadi, lekin yig'ish davom etadi.
)

REM --- 5. .exe yig'ish ---
echo [4/5] PyInstaller orqali .exe yig'ilmoqda...
pyinstaller --noconfirm --clean spektranaliz_eeg.spec
if errorlevel 1 (
    echo [XATO] .exe yig'ishda xatolik yuz berdi.
    pause
    exit /b 1
)

echo.
echo [TAYYOR] .exe yaratildi: dist\Spektranaliz EEG\Spektranaliz EEG.exe
echo.

REM --- 6. O'rnatuvchi (setup.exe) ni yasash (Inno Setup bo'lsa) ---
echo [5/5] O'rnatuvchi (setup.exe) tekshirilmoqda...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if defined ISCC (
    echo Inno Setup topildi. O'rnatuvchi yasalmoqda...
    "!ISCC!" installer.iss
    echo.
    echo [TAYYOR] O'rnatuvchi yaratildi: installer\Spektranaliz-EEG-Setup.exe
) else (
    echo [MA'LUMOT] Inno Setup topilmadi.
    echo            O'rnatuvchi (setup.exe) yasash uchun https://jrsoftware.org/isdl.php
    echo            dan Inno Setup 6 o'rnating va so'ng installer.iss faylini kompilyatsiya qiling.
)

echo.
echo ============================================================
echo   Jarayon yakunlandi.
echo ============================================================
pause
