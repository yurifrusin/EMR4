@echo off
if exist "%~dp0..\.venv\Scripts\python.exe" (
  "%~dp0..\.venv\Scripts\python.exe" "%~dp0ariadne_deepcode_notify.py" --outbox "%~dp0..\local_data\ariadne-harness\deepcode-outbox"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python "%~dp0ariadne_deepcode_notify.py" --outbox "%~dp0..\local_data\ariadne-harness\deepcode-outbox"
  ) else (
    py -3 "%~dp0ariadne_deepcode_notify.py" --outbox "%~dp0..\local_data\ariadne-harness\deepcode-outbox"
  )
)
