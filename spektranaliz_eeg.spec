# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spetsifikatsiya fayli - 'Spektranaliz EEG' dasturi uchun.

Yig'ish:
    pyinstaller spektranaliz_eeg.spec

Natija: dist/Spektranaliz EEG/Spektranaliz EEG.exe (papkali, onedir rejimi).
Resurslar (fon rasmlari, ikona, logolar) .exe yoniga bundle qilinadi.
"""

import os

block_cipher = None

# Agar ikona/logo rasterlari hali yo'q bo'lsa, ularni SVG dan avtomatik yasaymiz.
if not os.path.exists("spektranaliz-eeg-icon.ico"):
    import subprocess
    import sys as _sys
    print("[spec] Rasterlar topilmadi - make_assets.py ishga tushirilmoqda...")
    subprocess.run([_sys.executable, "make_assets.py"], check=False)

ICON_FILE = "spektranaliz-eeg-icon.ico" if os.path.exists("spektranaliz-eeg-icon.ico") else None

# Dastur yoniga qo'shiladigan resurs fayllar: (manba, .exe ichidagi joy).
# '.' - resurslar bundle ildiziga (resource_path() shu yerdan o'qiydi) joylanadi.
datas = [
    ("EEG spectrum background 700x700.svg", "."),
    ("EEG-spectrum-background-730x730.png", "."),
    ("EEG spectrum background 685x685.jpg", "."),
    ("spektranaliz-eeg-icon.svg", "."),
    ("spektranaliz-eeg-icon.ico", "."),
    ("spektranaliz-eeg-icon.png", "."),
    ("spektranaliz-eeg-logo.svg", "."),
    ("spektranaliz-eeg-logo-dark.svg", "."),
    ("spektranaliz-eeg-logo.png", "."),
    ("spektranaliz-eeg-logo-dark.png", "."),
]

# Faqat haqiqatan mavjud fayllarni qoldiramiz (ixtiyoriylari yo'q bo'lsa o'tkazib yuboriladi).
datas = [(src, dst) for (src, dst) in datas if os.path.exists(src)]

hiddenimports = [
    "PIL._tkinter_finder",
    "scipy.signal",
    "scipy.integrate",
    "pandas",
    "svglib",
    "reportlab",
    "pyedflib",
]

a = Analysis(
    ["Spektranaliz EEG+++.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["mne", "matplotlib", "tkinter.test", "pytest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Spektranaliz EEG",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI dasturi - konsol oynasi ko'rsatilmaydi
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Spektranaliz EEG",
    # Fayllarni "_internal" o'rniga to'g'ridan-to'g'ri dastur papkasi ildiziga
    # joylaymiz. Shunda o'rnatilgandan keyin resurslar (jumladan
    # spektranaliz-eeg-icon.ico) C:\Program Files\Spektranaliz EEG\ da bo'ladi
    # va yorliq ikonasi yo'li to'g'ri ishlaydi.
    contents_directory=".",
)
