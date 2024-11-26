# Variables
$sourceDir = "C:\Users\rmcmurry\Documents\GitHub\WestPi" 
$plinkCmd = "plink.exe -batch -pw raspberry pi@wpilibpi.local"
$pscpCmd = "pscp.exe -pw raspberry"

# Sync .py files
Write-Host "Syncing Navigator to Raspberry Pi..."
$localFile = "$sourceDir\DirectNavigator.py"
$remotePath = "pi@wpilibpi.local:./DirectNavigator.py"    
Invoke-Expression "$pscpCmd $localFile $remotePath"

# Restart the service
Write-Host "Restarting service on Raspberry Pi..."
Invoke-Expression "$plinkCmd 'sudo pkill -f uploaded.py'"

# Make filesystem read-only (optional)
Write-Host "Deployment complete!"
