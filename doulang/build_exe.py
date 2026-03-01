"""
打包豆语为独立可执行文件
"""

import PyInstaller.__main__
import os

# 打包配置
PyInstaller.__main__.run([
    'src/doulang/__main__.py',  # 入口文件
    '--name=doulang',            # 输出名称
    '--onefile',                 # 单个文件
    '--windowed',                # Windows无控制台
    '--icon=assets/icon.ico',    # 图标
    '--add-data=src/doulang:.',  # 包含源码
    '--hidden-import=chromadb',
    '--hidden-import=sentence_transformers',
    '--hidden-import=numpy',
    '--hidden-import=requests',
    '--clean',
    '--noconfirm',
])

print("✅ 打包完成！")
print("输出: dist/doulang.exe")
