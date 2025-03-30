# 염색도우미.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],  # 또는 절대 경로 사용 가능
    binaries=[],
    datas=[
        ('icon.png', '.'), 
        ('사용법.txt', '.')
    ],
    hiddenimports=[
        'sklearn',
        'sklearn.cluster',
        'sklearn.utils._openmp_helpers',
        'scipy.spatial.transform._rotation_groups',
        'scipy.linalg.cython_blas',

        # ✅ 현재 사용하는 내부 모듈
        'color_picker_ui',
        'controller',
        'detector',
        'region_selector',
        'color_util',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # ❌ 더 이상 사용하지 않는 것 있으면 여기에 명시 가능
        'tone_selector',
        'tone_utils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='염색도우미',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='염색도우미'
)
