; Amicus Theologi 1.0.8 – normal Windows wizard installer.
; Compiles after running the PyInstaller build from the repository root.
#define AppVersion "1.0.8"
#define AppName "Amicus Theologi"
[Setup]
AppId={{26A80230-4B69-4A47-A1CA-6F7425147101}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Amicus Theologi (Open-Source-Projekt)
AppCopyright=Open-Source-Projekt Amicus Theologi
DefaultDirName={localappdata}\Programs\Amicus Theologi
DefaultGroupName=Amicus Theologi
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\AmicusTheologi.exe
SetupIconFile=..\assets\amicus.ico
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
OutputDir=..\dist_installer
OutputBaseFilename=Amicus-Theologi-Setup-1.0.8
AllowNoIcons=no
ChangesAssociations=no
CloseApplications=yes
RestartApplications=no
LicenseFile=..\LICENSE
MinVersion=10.0

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktopverknüpfung erstellen"; GroupDescription: "Weitere Verknüpfungen:"; Flags: unchecked

[Files]
Source: "..\dist\AmicusTheologi\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Standalone manual available by direct double-click, also in the application.
Source: "..\ANLEITUNG.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ANLEITUNG.css"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\ANLEITUNG.js"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Amicus Theologi"; Filename: "{app}\AmicusTheologi.exe"; WorkingDir: "{app}"; IconFilename: "{app}\AmicusTheologi.exe"
Name: "{autoprograms}\Amicus Theologi – Handbuch"; Filename: "{app}\ANLEITUNG.html"
Name: "{autodesktop}\Amicus Theologi"; Filename: "{app}\AmicusTheologi.exe"; WorkingDir: "{app}"; IconFilename: "{app}\AmicusTheologi.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AmicusTheologi.exe"; Description: "Amicus Theologi jetzt starten"; Flags: nowait postinstall skipifsilent
