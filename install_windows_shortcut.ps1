# Einmalig ausfuehren: erstellt eine Windows-Desktopverknuepfung.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Amicus Theologi.lnk'))
$shortcut.TargetPath = Join-Path $root 'start_windows.bat'
$shortcut.WorkingDirectory = $root
$shortcut.Description = 'Amicus Theologi – wissenschaftliche Bibelarbeit'
$shortcut.Save()
Write-Host 'Desktopverknuepfung wurde erstellt.'
