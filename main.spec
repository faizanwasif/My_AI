# -*- mode: python ; coding: utf-8 -*-

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('src', 'src'), ('.env', '.')],
             hiddenimports=['crewai', 'crewai_tools', 'feedparser', 'langchain_anthropic', 'langchain_community', 'dotenv', 'PyQt6', 'PyQt6.sip', 'embedchain'],
             hookspath=['.'],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False)