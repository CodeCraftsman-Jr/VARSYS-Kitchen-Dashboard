; VARSYS Kitchen Dashboard Professional Installer Script
; Created with Inno Setup for professional Windows installation

#define MyAppName "VARSYS Kitchen Dashboard"
#define MyAppVersion "1.0.6"
#define MyAppPublisher "VARSYS Solutions"
#define MyAppURL "https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard"
#define MyAppExeName "VARSYS_Kitchen_Dashboard.exe"
#define MyAppServiceName "VARSYS_Kitchen_Service.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{8B5F4A2C-9D3E-4F1A-B2C7-8E9F0A1B2C3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\VARSYS Solutions\Kitchen Dashboard
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=VARSYS_Kitchen_Dashboard_v{#MyAppVersion}_Setup
SetupIconFile=assets\icons\vasanthkitchen.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Professional Kitchen Management System
VersionInfoCopyright=Copyright (C) 2025 VARSYS Solutions

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "autostart"; Description: "Start {#MyAppName} automatically when Windows starts"; GroupDescription: "Startup Options:"; Flags: checked

[Files]
; Main application executable
Source: "build\exe\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe\{#MyAppServiceName}"; DestDir: "{app}"; Flags: ignoreversion

; Application modules and data
Source: "build\exe\modules\*"; DestDir: "{app}\modules"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe\utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "build\exe\secure_credentials\*"; DestDir: "{app}\secure_credentials"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files
Source: "build\exe\firebase_web_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe\config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe\manifest.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe\__version__.py"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "RELEASE_NOTES.md"; DestDir: "{app}"; Flags: ignoreversion

; Python runtime and dependencies (if using cx_Freeze)
Source: "build\exe\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{src}\build\exe\lib'))

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\vasanthkitchen.ico"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icons\vasanthkitchen.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Auto-startup registry entry (if selected)
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "VARSYS_Kitchen_Dashboard"; ValueData: """{app}\{#MyAppServiceName}"""; Flags: uninsdeletevalue; Tasks: autostart

; Application registration
Root: HKLM; Subkey: "SOFTWARE\VARSYS Solutions\Kitchen Dashboard"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\VARSYS Solutions\Kitchen Dashboard"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

[Run]
; Start the system tray service after installation
Filename: "{app}\{#MyAppServiceName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop the service before uninstalling
Filename: "taskkill"; Parameters: "/F /IM {#MyAppServiceName}"; Flags: runhidden; RunOnceId: "StopService"
Filename: "taskkill"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "StopMainApp"

[UninstallDelete]
; Clean up user data (optional - ask user)
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\data_backup"
Type: files; Name: "{app}\last_update_check.json"

[Code]
function DirExists(DirName: String): Boolean;
begin
  Result := DirExists(DirName);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if application is running and ask to close it
  if CheckForMutexes('VARSYS_Kitchen_Dashboard_Mutex') then
  begin
    if MsgBox('VARSYS Kitchen Dashboard is currently running. Please close it before continuing with the installation.', 
              mbConfirmation, MB_OKCANCEL) = IDCANCEL then
    begin
      Result := False;
      Exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create application mutex for single instance
    // This will be handled by the application itself
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Ask user about keeping user data
  if MsgBox('Do you want to keep your Kitchen Dashboard data and settings?', 
            mbConfirmation, MB_YESNO) = IDYES then
  begin
    // Don't delete user data
    Result := True;
  end
  else
  begin
    // Delete all data
    Result := True;
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nVARSYS Kitchen Dashboard is a professional kitchen management system with cloud synchronization and subscription-based access.%n%nIt is recommended that you close all other applications before continuing.
FinishedHeadingLabel=Completing the [name] Setup Wizard
FinishedLabelNoIcons=Setup has finished installing [name] on your computer. The application will start automatically in the system tray.
FinishedLabel=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed icons.
ClickFinish=Click Finish to exit Setup and start using VARSYS Kitchen Dashboard.
