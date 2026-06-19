@echo off
REM MiniOS Build Script
REM Assembles boot sector + kernel, creates bootable floppy image

set PROJECT_DIR=%~dp0
set NASM="D:\Program Files\NASM\nasm.exe"

echo ========================================
echo  MiniOS Build Script
echo ========================================
echo.

REM Step 1: Assemble boot sector
echo [1/3] Assembling boot sector...
%NASM% -f bin "%PROJECT_DIR%boot.asm" -o "%PROJECT_DIR%build\boot.bin"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Boot sector assembly failed!
    exit /b 1
)
echo   OK - boot.bin (512 bytes)

REM Step 2: Assemble kernel
echo [2/3] Assembling kernel...
%NASM% -f bin "%PROJECT_DIR%kernel.asm" -o "%PROJECT_DIR%build\kernel.bin"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Kernel assembly failed!
    exit /b 1
)
echo   OK - kernel.bin (%date% %time%)

REM Step 3: Create disk image
echo [3/3] Creating disk image...
set IMG_FILE=%PROJECT_DIR%build\minios.img

REM Create empty 1.44MB floppy image (2880 sectors * 512 bytes)
REM Using PowerShell to create the file
powershell -Command "$f = [System.IO.File]::Create('%IMG_FILE:\=\\%'); $f.SetLength(1474560); $f.Close()"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create disk image!
    exit /b 1
)

REM Write boot sector to sector 0
%NASM% -f bin -o "%PROJECT_DIR%build\boot_only.bin" "%PROJECT_DIR%boot.asm"
powershell -Command "$b = [System.IO.File]::ReadAllBytes('%PROJECT_DIR%build\boot_only.bin'); $i = [System.IO.File]::ReadAllBytes('%IMG_FILE:\=\\%'); for($j=0;$j -lt $b.Length;$j++) { $i[$j] = $b[$j] }; [System.IO.File]::WriteAllBytes('%IMG_FILE:\=\\%', $i)"

REM Write kernel starting at sector 1 (offset 512)
powershell -Command "$k = [System.IO.File]::ReadAllBytes('%PROJECT_DIR%build\kernel.bin'); $i = [System.IO.File]::ReadAllBytes('%IMG_FILE:\=\\%'); for($j=0;$j -lt $k.Length;$j++) { $i[512+$j] = $k[$j] }; [System.IO.File]::WriteAllBytes('%IMG_FILE:\=\\%', $i)"

echo   OK - minios.img (1.44MB floppy image)
echo.
echo ========================================
echo  Build complete!
echo.
echo  Image: %IMG_FILE%
echo.
echo  To run in QEMU:
echo    qemu-system-i386 -fda build\minios.img
echo.
echo  To run in VirtualBox:
echo    Create new VM - Type: Other, Version: Other/Unknown
echo    Set FDD to minios.img
echo ========================================
echo.

REM Clean up temp files
del "%PROJECT_DIR%build\boot_only.bin" 2>nul
