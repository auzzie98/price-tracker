@echo off
set AZCLI="C:\\Program Files\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd"
cd C:\Users\auzzi\OneDrive\Desktop\price-tracker
%AZCLI% webapp config set --name price-tracker-auzzie98 --resource-group price-tracker-rg --startup-file "python -m uvicorn price_tracker.app:app --host 0.0.0.0 --port %PORT%"
echo Done