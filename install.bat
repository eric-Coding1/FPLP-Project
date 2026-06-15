@echo off
chcp 65001 >nul
title FPLP v1.0 安装程序
color 0B

echo ╔══════════════════════════════════════╗
echo ║    FPLP - Fast Parallel Language Plus  ║
echo ║    正在安装...                        ║
echo ╚══════════════════════════════════════╝
echo.

:: --- 检测 Python ---
echo [1/5] 检测 Python 环境...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [错误] 未检测到 Python！请先安装 Python 3.10+
    echo        下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo        Python %PY_VER% ✓
echo.

:: --- 设置安装路径 ---
set INSTALL_DIR=%USERPROFILE%\FPLP
echo [2/5] 安装目录：%INSTALL_DIR%

:: --- 创建目录并复制文件 ---
echo [3/5] 复制文件...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\fplp" mkdir "%INSTALL_DIR%\fplp"

:: 复制核心模块
xcopy /E /Y /Q "%~dp0fplp\*.py" "%INSTALL_DIR%\fplp\" >nul 2>&1
echo        fplp\ 模块 ✓

:: 复制入口文件
copy /Y "%~dp0main.py" "%INSTALL_DIR%\" >nul 2>&1
echo        main.py ✓
copy /Y "%~dp0fplp.bat" "%INSTALL_DIR%\" >nul 2>&1
echo        fplp.bat ✓

:: 复制示例
if exist "%~dp0examples" (
    if not exist "%INSTALL_DIR%\examples" mkdir "%INSTALL_DIR%\examples"
    xcopy /E /Y /Q "%~dp0examples\*.fplp" "%INSTALL_DIR%\examples\" >nul 2>&1
    echo        examples\ ✓
)

:: 复制文档
copy /Y "%~dp0README.md" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "%~dp0README_en.md" "%INSTALL_DIR%\" >nul 2>&1
if exist "%~dp0fplp_icon.png" copy /Y "%~dp0fplp_icon.png" "%INSTALL_DIR%\" >nul 2>&1
echo        文档 ✓
echo.

:: --- 安装 Pillow ---
echo [4/5] 安装 Pillow 图形库（首次需要，约 5-10 秒）...
python -m pip install Pillow -q >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo        Pillow ✓
) else (
    echo        [警告] Pillow 安装失败，图形功能不可用
    echo        可用：pip install Pillow
)
echo.

:: --- 创建快捷方式 ---
echo [5/5] 创建桌面快捷方式...
set SHORTCUT=%USERPROFILE%\Desktop\FPLP.lnk
> "%TEMP%\mklnk.vbs" echo Set WshShell = CreateObject("WScript.Shell")
>>"%TEMP%\mklnk.vbs" echo Set Link = WshShell.CreateShortcut("%SHORTCUT%")
>>"%TEMP%\mklnk.vbs" echo Link.Description = "FPLP - Fast Parallel Language Plus"
>>"%TEMP%\mklnk.vbs" echo Link.TargetPath = "%INSTALL_DIR%\fplp.bat"
>>"%TEMP%\mklnk.vbs" echo Link.WorkingDirectory = "%INSTALL_DIR%"
>>"%TEMP%\mklnk.vbs" echo Link.IconLocation = "%INSTALL_DIR%\fplp_icon.png"
>>"%TEMP%\mklnk.vbs" echo Link.Save
cscript //nologo "%TEMP%\mklnk.vbs" >nul 2>&1
del "%TEMP%\mklnk.vbs" >nul 2>&1
echo        桌面快捷方式 ✓

:: --- 添加到 PATH ---
echo. >> "%TEMP%\fplp_path.txt"
setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
echo        已添加到 PATH ✓
echo.

:: --- 完成 ---
echo ╔══════════════════════════════════════╗
echo ║      FPLP 安装完成！                   ║
echo ║                                       ║
echo ║  启动方式：                            ║
echo ║    • 双击桌面 FPLP 图标               ║
echo ║    • 命令行输入：fplp.bat              ║
echo ║    • 命令行输入：python main.py        ║
echo ║                                       ║
echo ║  FPLP 使用指南已复制到安装目录         ║
echo ╚══════════════════════════════════════╝
echo.

pause
