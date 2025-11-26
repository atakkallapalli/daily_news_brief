# install-git.ps1
# Download the Git installer
$gitInstallerUrl = "https://download-mirror.github.com/git-for-windows/v2.36.0.windows.1/git-2.36.0-64-bit.exe"
$gitInstallerFile = "$env:TEMP\git-installer.exe"
Invoke-WebRequest -Uri $gitInstallerUrl -OutFile $gitInstallerFile

# Install Git
Start-Process -FilePath $gitInstallerFile -Wait -ArgumentList '/VERYSILENT', '/NOSTARTMENU', '/NOCLOSE', '/DIR="C:\Program Files\Git"'

# Add Git to the PATH environment variable
$gitPath = "C:\Program Files\Git\bin"
$pathEnvVar = [Environment]::GetEnvironmentVariable("PATH", "Machine")
$newPath = $pathEnvVar -replace ';', ':' -join "`,$gitPath"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")

# Remove the installer file
Remove-Item -Path $gitInstallerFile
