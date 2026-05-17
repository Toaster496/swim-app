# PyInstaller spec file for SwimScore Windows executable
# Build with: pyinstaller swimscore.spec

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('swimapp/templates', 'swimapp/templates'),
        ('swimapp/static', 'swimapp/static'),
        ('instance', 'instance'),
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'werkzeug.security',
        'werkzeug.serving',
        'jinja2',
        'markupsafe',
        'sqlalchemy',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SwimScore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SwimScore',
)
