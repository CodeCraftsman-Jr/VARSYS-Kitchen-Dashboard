[Setup]
; Basic application information
AppId={{12345678-1234-5678-9012-123456789012}
AppName=VARSYS Kitchen Dashboard
AppVersion=1.0.6
AppVerName=VARSYS Kitchen Dashboard v1.0.6
AppPublisher=VARSYS
AppPublisherURL=https://varsys.com
AppSupportURL=https://varsys.com/support
AppUpdatesURL=https://varsys.com/updates
AppCopyright=Copyright (C) 2025 VARSYS

; Installation directories
DefaultDirName={autopf}\VARSYS\Kitchen Dashboard
DefaultGroupName=VARSYS Kitchen Dashboard
AllowNoIcons=yes

; Output configuration
OutputDir=installer_output
OutputBaseFilename=VARSYS_Kitchen_Dashboard_v1.0.6_Setup
SetupIconFile=assets\icons\vasanthkitchen.ico
Compression=lzma
SolidCompression=yes

; Windows version requirements
MinVersion=10.0.17763
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges and behavior
PrivilegesRequired=admin
DisableProgramGroupPage=yes
DisableWelcomePage=no
DisableFinishedPage=no

; License and information
LicenseFile=LICENSE
InfoBeforeFile=README.md

; Uninstall configuration
UninstallDisplayIcon={app}\VARSYS_Kitchen_Dashboard.exe
UninstallDisplayName=VARSYS Kitchen Dashboard v1.0.6

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startup"; Description: "Start with Windows"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
; Main executable and all dependencies from cx_Freeze build
Source: "build\exe.win-amd64-*\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Additional files
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VARSYS Kitchen Dashboard"; Filename: "{app}\VARSYS_Kitchen_Dashboard.exe"
Name: "{group}\{cm:UninstallProgram,VARSYS Kitchen Dashboard}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\VARSYS Kitchen Dashboard"; Filename: "{app}\VARSYS_Kitchen_Dashboard.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\VARSYS Kitchen Dashboard"; Filename: "{app}\VARSYS_Kitchen_Dashboard.exe"; Tasks: quicklaunchicon

[Registry]
; Auto-startup registry entry
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "VARSYS Kitchen Dashboard"; ValueData: """{app}\VARSYS_Kitchen_Dashboard.exe"" --startup"; Flags: uninsdeletevalue; Tasks: startup

; File associations (optional)
Root: HKCR; Subkey: ".kitchen"; ValueType: string; ValueName: ""; ValueData: "VARSYSKitchenFile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VARSYSKitchenFile"; ValueType: string; ValueName: ""; ValueData: "VARSYS Kitchen Dashboard File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VARSYSKitchenFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\VARSYS_Kitchen_Dashboard.exe,0"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VARSYSKitchenFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\VARSYS_Kitchen_Dashboard.exe"" ""%1"""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\VARSYS_Kitchen_Dashboard.exe"; Description: "{cm:LaunchProgram,VARSYS Kitchen Dashboard}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\data\*.log"
Type: files; Name: "{app}\*.tmp"

[Code]
function IsUpgrade: Boolean;
var
  Value: string;
begin
  Result := RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1', 'UninstallString', Value) or
            RegQueryStringValue(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1', 'UninstallString', Value);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create application data directories
    CreateDir(ExpandConstant('{userappdata}\VARSYS\Kitchen Dashboard'));
    CreateDir(ExpandConstant('{userappdata}\VARSYS\Kitchen Dashboard\logs'));
    CreateDir(ExpandConstant('{userappdata}\VARSYS\Kitchen Dashboard\data'));
  end;
end;

function InitializeSetup: Boolean;
begin
  Result := True;
  if IsUpgrade then
  begin
    if MsgBox('A previous version of VARSYS Kitchen Dashboard is installed. Do you want to upgrade?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;
