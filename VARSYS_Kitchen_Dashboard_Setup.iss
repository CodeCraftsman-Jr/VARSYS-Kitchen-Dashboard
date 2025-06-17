; VARSYS Kitchen Dashboard - Inno Setup Script
; Professional Windows Installer for Kitchen Dashboard Application
; Created for cx_Freeze build output

#define MyAppName "VARSYS Kitchen Dashboard"
#define MyAppVersion "1.1.3"
#define MyAppPublisher "VARSYS Technologies"
#define MyAppURL "https://github.com/VARSYS/Kitchen-Dashboard"
#define MyAppExeName "VARSYS_Kitchen_Dashboard.exe"
#define MyAppDescription "Professional Kitchen Management Dashboard with Firebase Cloud Sync"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{8B2F4A3C-9D1E-4F5A-B6C7-2E8F9A0B1C2D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=VARSYS_Kitchen_Dashboard_v{#MyAppVersion}_Setup
; SetupIconFile=vasanthkitchen.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Uninstall settings
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Version information
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startup"; Description: "Start {#MyAppName} with Windows"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
; Main executable
Source: "build\exe.win-amd64-3.12\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Python runtime DLLs
Source: "build\exe.win-amd64-3.12\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\python312.dll"; DestDir: "{app}"; Flags: ignoreversion

; Library directory (all compiled modules and dependencies)
Source: "build\exe.win-amd64-3.12\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs

; Application modules
Source: "build\exe.win-amd64-3.12\modules\*"; DestDir: "{app}\modules"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\tests\*"; DestDir: "{app}\tests"; Flags: ignoreversion recursesubdirs createallsubdirs

; Data directories
Source: "build\exe.win-amd64-3.12\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\data_backup\*"; DestDir: "{app}\data_backup"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\reports\*"; DestDir: "{app}\reports"; Flags: ignoreversion recursesubdirs createallsubdirs

; Assets and resources
Source: "build\exe.win-amd64-3.12\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files
Source: "build\exe.win-amd64-3.12\*.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\*.key"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\*.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\*.txt"; DestDir: "{app}"; Flags: ignoreversion

; Python scripts and utilities
Source: "build\exe.win-amd64-3.12\*.py"; DestDir: "{app}"; Flags: ignoreversion

; Batch and shell scripts
Source: "build\exe.win-amd64-3.12\*.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\*.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\*.sh"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "build\exe.win-amd64-3.12\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.12\FIREBASE_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion

; Secure credentials directory
Source: "build\exe.win-amd64-3.12\secure_credentials\*"; DestDir: "{app}\secure_credentials"; Flags: ignoreversion recursesubdirs createallsubdirs

; Release tools and documentation
Source: "build\exe.win-amd64-3.12\release_tools\*"; DestDir: "{app}\release_tools"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\releases\*"; DestDir: "{app}\releases"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe.win-amd64-3.12\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

; Cache directories
Source: "build\exe.win-amd64-3.12\__pycache__\*"; DestDir: "{app}\__pycache__"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\vasanthkitchen.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\vasanthkitchen.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\vasanthkitchen.ico"; Tasks: quicklaunchicon

[Registry]
; Add to Windows startup if selected
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

; File associations (optional - for future use)
Root: HKCR; Subkey: ".kitchen"; ValueType: string; ValueName: ""; ValueData: "KitchenDashboardFile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "KitchenDashboardFile"; ValueType: string; ValueName: ""; ValueData: "Kitchen Dashboard Data File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "KitchenDashboardFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "KitchenDashboardFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\modules\__pycache__"
Type: filesandordirs; Name: "{app}\utils\__pycache__"

[Code]
// Custom installation procedures
procedure InitializeWizard;
begin
  // Custom welcome message
  WizardForm.WelcomeLabel2.Caption := 
    'This will install {#MyAppName} {#MyAppVersion} on your computer.' + #13#10#13#10 +
    'Kitchen Dashboard is a professional kitchen management application with Firebase cloud sync capabilities.' + #13#10#13#10 +
    'It is recommended that you close all other applications before continuing.';
end;

function InitializeSetup(): Boolean;
begin
  // Check for minimum Windows version (Windows 10)
  if not IsWin64 then begin
    MsgBox('This application requires a 64-bit version of Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end else begin
    Result := True;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    // Create application data directories if they don't exist
    ForceDirectories(ExpandConstant('{userappdata}\{#MyAppName}'));
    ForceDirectories(ExpandConstant('{userappdata}\{#MyAppName}\backups'));
    ForceDirectories(ExpandConstant('{userappdata}\{#MyAppName}\logs'));
  end;
end;
