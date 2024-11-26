Param(
    [string] $mainFile = "WestPi.py"
)

# Variables
$sourceDir = "C:\Users\rmcmurry\Documents\GitHub\WestPi\" 
$plinkCmd = "plink.exe -batch -pw raspberry pi@wpilibpi.local"
$pscpCmd = "pscp.exe -pw raspberry"

Write-Host "Copying $mainFile to uploaded.py"
Copy-Item -Path "$sourceDir\$mainFile" -Destination "$sourceDir\uploaded.py" -Force

# Make filesystem writable
Write-Host "Making filesystem writable on Raspberry Pi..."
Invoke-Expression "$plinkCmd 'sudo mount -o remount,rw /'"

Start-Sleep -Seconds 2

# Sync .py files
Write-Host "Syncing files to Raspberry Pi..."
Get-ChildItem -Path $sourceDir -Filter *.py | ForEach-Object {
    $localFile = $_.FullName
    $remotePath = "pi@wpilibpi.local:./$($_.Name)"    
    Invoke-Expression "$pscpCmd $localFile $remotePath"
    Start-Sleep -Seconds 0.5
}

# Restart the service
Write-Host "Restarting service on Raspberry Pi..."
Invoke-Expression "$plinkCmd 'sudo pkill -f uploaded.py'"

# Make filesystem read-only (optional)
# Write-Host "Making filesystem read-only on Raspberry Pi..."
Invoke-Expression "$plinkCmd 'sudo mount -o remount,ro /'"

Write-Host "Deployment complete!"
