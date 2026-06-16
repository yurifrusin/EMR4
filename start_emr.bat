@echo off
:: EMR4 dev stack launcher — shim for run_dev.ps1
:: Double-click this or call it with any run_dev.ps1 flags: start_emr.bat -NoDevServer
powershell -ExecutionPolicy Bypass -File "%~dp0run_dev.ps1" %*
