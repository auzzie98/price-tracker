import subprocess
result = subprocess.run([".\\venv\\Scripts\\python.exe", "scripts\\build_derived.py", "--rebuild"], cwd="C:\\Users\\auzzi\\OneDrive\\Desktop\\price-tracker")
print("Return code:", result.returncode)