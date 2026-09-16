$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcherPath = Join-Path $projectDir "start_bot.bat"
$iconPath = Join-Path $projectDir "assets\cat-home-tasker.ico"
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Cat Home Tasker.lnk"

if (-not (Test-Path $launcherPath)) {
    throw "Файл start_bot.bat не найден."
}

if (-not (Test-Path $iconPath)) {
    throw "Файл иконки не найден."
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)

$shortcut.TargetPath = $launcherPath
$shortcut.WorkingDirectory = $projectDir
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Telegram bot for household task management"
$shortcut.Save()

Write-Host "Shortcut created: $shortcutPath"