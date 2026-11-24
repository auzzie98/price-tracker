import subprocess
import sys

az_cmd = r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd'

# Set the startup file for the Azure Web App
print("Setting startup command...")
r = subprocess.run([az_cmd, 'webapp', 'config', 'set', '--name', 'price-tracker-auzzie98', '--resource-group', 'price-tracker-rg', '--startup-file', 'python -m uvicorn price_tracker.app:app --host 0.0.0.0 --port $PORT'], capture_output=True, text=True)
print('RC:', r.returncode)
print('STDOUT:', r.stdout)
print('STDERR:', r.stderr)

# Verify the config was set
print("\nVerifying config...")
r = subprocess.run([az_cmd, 'webapp', 'config', 'show', '--name', 'price-tracker-auzzie98', '--resource-group', 'price-tracker-rg'], capture_output=True, text=True)
print('RC:', r.returncode)
# Find appCommandLine in the output
for line in r.stdout.split('\n'):
    if 'appCommandLine' in line:
        print('Startup command:', line.strip())