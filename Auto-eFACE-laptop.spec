# -*- mode: python -*-

block_cipher = None


a = Analysis(['Auto-eFACE.py'],
             pathex=['C:\\Users\\guarind\\Documents\\GitHub\\Auto-eFace'],
             binaries=[],
             datas=[],
             hiddenimports=[PyQt5],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='auto-eFACE',
          debug=False,
          strip=False,
          upx=True,
          console=False, icon='meei_3WR_icon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='auto-eFACE')
