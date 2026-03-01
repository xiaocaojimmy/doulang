@echo off
chcp 65001 > nul
title 豆语一键安装

echo.
echo ========================================
echo     🧠 豆语 DouLang 一键安装
echo ========================================
echo.

:: 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python
    echo.
    echo 请先安装Python 3.8+: https://python.org/downloads
    echo 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python已安装

:: 安装豆语
echo.
echo 📦 正在安装豆语...
pip install -q git+https://github.com/xiaocaojimmy/doulang.git
if errorlevel 1 (
    echo ⚠️  从GitHub安装失败，尝试备用方式...
    pip install -q chromadb sentence-transformers requests numpy
)

:: 创建启动器
echo.
echo 🚀 创建桌面快捷方式...

set "DESKTOP=%USERPROFILE%\Desktop"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

(
echo @echo off
echo chcp 65001 > nul
echo echo 🧠 启动豆语...
echo echo.
echo python -c "from doulang import DouLangEnhanced; dl = DouLangEnhanced(); print('豆语已启动！'); print('使用: result = dl.chat_with_memory(%%'你的问题%%')'); print('查看记忆: dl.recall(%%'关键词%%')')"
echo echo.
echo pause
) > "%DESKTOP%\启动豆语.bat"

(
echo @echo off
echo start "" "%%USERPROFILE%%\Desktop\启动豆语.bat"
) > "%STARTUP%\doulang-startup.bat"

echo ✅ 桌面快捷方式已创建

:: 检查Ollama
echo.
echo 🔍 检查Ollama...
curl -s http://localhost:11434/api/tags > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama未运行
    echo.
    echo 请按以下步骤操作：
    echo 1. 下载Ollama: https://ollama.com/download
    echo 2. 安装后运行: ollama serve
    echo 3. 然后双击桌面的"启动豆语.bat"
) else (
    echo ✅ Ollama运行中
)

echo.
echo ========================================
echo     🎉 安装完成！
echo ========================================
echo.
echo 使用方式：
echo   1. 确保Ollama运行: ollama serve
echo   2. 双击桌面"启动豆语.bat"
echo.
echo 或者直接打开Python：
echo   from doulang import DouLangEnhanced
echo   dl = DouLangEnhanced()
echo   dl.chat_with_memory("我是谁？")
echo.

pause
