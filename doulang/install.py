#!/usr/bin/env python3
"""
豆语一键安装脚本
支持: Windows/macOS/Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    print("="*60)
    print("🧠 豆语 DouLang 一键安装")
    print("="*60)
    print()

def check_python():
    """检查Python版本"""
    print("📋 检查Python环境...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python版本过低: {version.major}.{version.minor}")
        print("   请安装Python 3.8或更高版本: https://python.org")
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    deps = [
        "chromadb",
        "sentence-transformers",
        "requests",
        "numpy"
    ]
    
    for dep in deps:
        print(f"   安装 {dep}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", dep],
                check=True,
                capture_output=True
            )
            print(f"   ✅ {dep}")
        except:
            print(f"   ⚠️  {dep} 安装失败，尝试备用源...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-i", 
                 "https://pypi.tuna.tsinghua.edu.cn/simple", dep],
                check=False
            )

def setup_doulang():
    """设置豆语"""
    print("🔧 设置豆语...")
    
    # 创建安装目录
    home = Path.home()
    install_dir = home / ".doulang"
    install_dir.mkdir(exist_ok=True)
    
    # 创建数据目录
    data_dir = install_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 创建配置文件
    config_file = install_dir / "config.json"
    if not config_file.exists():
        import json
        config = {
            "data_dir": str(data_dir),
            "ollama_host": "http://localhost:11434",
            "version": "2.1.0"
        }
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    print(f"   ✅ 安装目录: {install_dir}")
    print(f"   ✅ 数据目录: {data_dir}")

def create_launcher():
    """创建启动器"""
    print("🚀 创建启动器...")
    
    home = Path.home()
    install_dir = home / ".doulang"
    
    system = platform.system()
    
    if system == "Windows":
        # Windows .bat
        bat_file = install_dir / "doulang.bat"
        with open(bat_file, "w") as f:
            f.write("""@echo off
chcp 65001 >nul
echo 🧠 启动豆语...
cd /d "%~dp0"
python -c "from doulang import DouLangEnhanced; dl = DouLangEnhanced(); print('豆语已启动！'); print('使用: dl.chat_with_memory(\"你的问题\")')"
pause
""")
        print(f"   ✅ 启动器: {bat_file}")
        print(f"   使用方式: 双击 {bat_file.name}")
        
    else:
        # macOS/Linux .sh
        sh_file = install_dir / "doulang.sh"
        with open(sh_file, "w") as f:
            f.write("""#!/bin/bash
echo "🧠 启动豆语..."
cd "$(dirname "$0")"
python3 -c "from doulang import DouLangEnhanced; dl = DouLangEnhanced(); print('豆语已启动！')"
""")
        os.chmod(sh_file, 0o755)
        print(f"   ✅ 启动器: {sh_file}")
        print(f"   使用方式: ./{sh_file.name}")

def check_ollama():
    """检查Ollama"""
    print("🔍 检查Ollama...")
    try:
        import urllib.request
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            print("   ✅ Ollama运行中")
            return True
    except:
        print("   ⚠️  Ollama未检测到")
        print("   请先安装Ollama: https://ollama.com/download")
        print("   安装后运行: ollama serve")
        return False

def main():
    print_banner()
    
    # 检查Python
    if not check_python():
        sys.exit(1)
    
    # 安装依赖
    install_dependencies()
    
    # 设置豆语
    setup_doulang()
    
    # 创建启动器
    create_launcher()
    
    # 检查Ollama
    has_ollama = check_ollama()
    
    print()
    print("="*60)
    print("🎉 安装完成!")
    print("="*60)
    print()
    print("快速开始:")
    print("  1. 确保Ollama运行: ollama serve")
    print("  2. 启动豆语: 双击 ~/.doulang/doulang.bat (Windows)")
    print("            或 ~/.doulang/doulang.sh (macOS/Linux)")
    print()
    print("或者直接在Python中使用:")
    print("  from doulang import DouLangEnhanced")
    print("  dl = DouLangEnhanced()")
    print("  dl.chat_with_memory('我是做什么的？')")
    print()
    
    if not has_ollama:
        print("⚠️  注意: Ollama未运行，请先安装并启动Ollama")
        print("   下载: https://ollama.com/download")
    
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()
