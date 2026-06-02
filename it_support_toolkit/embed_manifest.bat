@echo off
set EXE_PATH=dist\ITSupportToolkit.exe
set MANIFEST_PATH=build_manifest.xml
set FOUND_MT=

if exist "%EXE_PATH%" (
    if exist "%MANIFEST_PATH%" (
        echo Embedding manifest for admin rights...

        where mt.exe 2>nul >nul
        if !errorlevel! equ 0 (
            set FOUND_MT=1
            mt.exe -manifest "%MANIFEST_PATH%" -outputresource:"%EXE_PATH%;#1"
            echo [OK] Manifest embedded
        )

        if not defined FOUND_MT (
            for %%P in (
                "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\mt.exe"
                "C:\Program Files (x86)\Windows Kits\10\bin\10.0.20348.0\x64\mt.exe"
                "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\mt.exe"
                "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\mt.exe"
            ) do (
                if exist %%P (
                    set FOUND_MT=1
                    %%P -manifest "%MANIFEST_PATH%" -outputresource:"%EXE_PATH%;#1"
                    echo [OK] Manifest embedded
                    goto :done
                )
            )
        )

        :done
        if not defined FOUND_MT (
            echo [WARN] mt.exe not found - EXE will not auto-elevate
        )
    )
)
