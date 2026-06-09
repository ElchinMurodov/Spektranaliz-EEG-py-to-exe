; ============================================================================
;  Spektranaliz EEG - Inno Setup o'rnatuvchi (setup.exe) skripti
;  Mualliflik: Murodov Elchin O'ktamovich
;
;  Bu skript dist/Spektranaliz EEG/ papkasidagi yig'ilgan dasturni yagona
;  "Spektranaliz-EEG-Setup.exe" o'rnatuvchi faylga joylaydi. O'rnatuvchi
;  Start Menu va Ish stoli yorliqlarini ikonka bilan yaratadi.
;
;  Kompilyatsiya:
;    1) Inno Setup o'rnating: https://jrsoftware.org/isdl.php
;    2) Ushbu faylni Inno Setup Compiler'da oching va "Compile" bosing,
;       yoki buyruq qatorida:  ISCC.exe installer.iss
; ============================================================================

#define MyAppName "Spektranaliz EEG"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Murodov Elchin O'ktamovich"
#define MyAppExeName "Spektranaliz EEG.exe"
#define MyBuildDir "dist\Spektranaliz EEG"

[Setup]
AppId={{8F3B2C9A-4D5E-4A1B-9C7D-EEG2025SPEKTR}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Spektranaliz-EEG-Setup
OutputDir=installer
SetupIconFile=spektranaliz-eeg-icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "uzbek"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Ish stolida yorliq yaratish"; GroupDescription: "Qo'shimcha yorliqlar:"; Flags: checkedonce

[Files]
; Yig'ilgan dasturning barcha fayllari (.exe, kutubxonalar, resurslar).
Source: "{#MyBuildDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
; Ikonani dastur papkasi ildiziga kafolatlangan nusxalaymiz - yorliqlar va
; .exe yuzidagi ikona yo'li doimo to'g'ri bo'lishi uchun (PyInstaller fayllarni
; "_internal" ga joylasa ham, bu nusxa {app} ildizida turadi).
Source: "spektranaliz-eeg-icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu yorlig'i (ikona {app} ildizidagi .ico dan)
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\spektranaliz-eeg-icon.ico"; WorkingDir: "{app}"
; Dasturni o'chirish yorlig'i
Name: "{group}\{#MyAppName} dasturini o'chirish"; Filename: "{uninstallexe}"
; Ish stoli yorlig'i (foydalanuvchi tanlasa)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\spektranaliz-eeg-icon.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; O'rnatish tugagach dasturni ishga tushirish imkoni
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} dasturini ishga tushirish"; Flags: nowait postinstall skipifsilent
