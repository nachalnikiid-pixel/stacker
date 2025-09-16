#!/usr/bin/env python3
"""
Скрипт для создания .exe файла из стакера наказаний
Требует установленный PyInstaller
"""

import os
import sys
import subprocess

def build_exe():
    """Создает .exe файл из Python приложения"""
    
    print("🏗️  Создание .exe файла для MAJESTIC Punishment Stacker...")
    print("by peep (discord: peepletmebleed)")
    print("─" * 50)
    
    # Проверяем наличие PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller найден")
    except ImportError:
        print("❌ PyInstaller не найден")
        print("Установите его командой: pip install pyinstaller")
        return False
    
    # Параметры для PyInstaller
    exe_name = "MAJESTIC_Punishment_Stacker"
    script_file = "run_stacker.py"
    
    if not os.path.exists(script_file):
        print(f"❌ Файл {script_file} не найден")
        return False
    
    print(f"📦 Создаем {exe_name}.exe...")
    
    # Команда PyInstaller с настройками
    cmd = [
        "pyinstaller",
        "--onefile",                    # Один исполняемый файл
        "--windowed",                   # Без консоли (для GUI)
        "--name", exe_name,             # Имя .exe файла
        "--icon=NONE",                  # Без иконки (можно добавить .ico файл)
        "--add-data", "test_commands.txt;.",     # Добавить тестовые команды
        "--add-data", "real_commands.txt;.",     # Добавить реальные команды
        "--hidden-import", "tkinter",            # Явно включить tkinter
        "--hidden-import", "tkinter.ttk",        # И ttk
        script_file
    ]
    
    try:
        # Запускаем PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ .exe файл создан успешно!")
            print(f"📁 Местоположение: dist/{exe_name}.exe")
            
            # Проверяем размер файла
            exe_path = f"dist/{exe_name}.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 Размер файла: {size_mb:.1f} MB")
            
            print("\n🎯 Готово! Теперь вы можете:")
            print(f"  • Запустить dist/{exe_name}.exe")
            print("  • Скопировать .exe файл на любой Windows компьютер")
            print("  • Использовать без установки Python")
            
            return True
        else:
            print("❌ Ошибка создания .exe файла:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def create_spec_file():
    """Создает файл .spec для настройки PyInstaller"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run_stacker.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('test_commands.txt', '.'),
        ('real_commands.txt', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MAJESTIC_Punishment_Stacker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open("stacker.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("📝 Создан файл stacker.spec для настройки")

if __name__ == "__main__":
    print("🏰 MAJESTIC Punishment Stacker - Сборка .exe")
    print("\nВыберите опцию:")
    print("1. Создать .exe файл автоматически")
    print("2. Создать .spec файл для настройки")
    print("3. Показать инструкции")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    if choice == "1":
        build_exe()
    elif choice == "2":
        create_spec_file()
        print("Теперь выполните: pyinstaller stacker.spec")
    elif choice == "3":
        print("\n📋 Инструкции для создания .exe:")
        print("1. Установите Python 3.7+ на Windows")
        print("2. pip install pyinstaller")
        print("3. python build_exe.py")
        print("4. Найдите .exe в папке dist/")
    else:
        print("❌ Неверный выбор")