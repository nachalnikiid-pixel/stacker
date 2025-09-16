# 🏗️ Инструкции по созданию .exe файла

## Автоматическая сборка

### На Windows:
```bash
# 1. Установить PyInstaller
pip install pyinstaller

# 2. Запустить скрипт сборки
python build_exe.py

# 3. Найти готовый .exe в папке dist/
```

### Ручная сборка:
```bash
pyinstaller --onefile --windowed --name "MAJESTIC_Punishment_Stacker" run_stacker.py
```

## Требования

- **Python 3.7+** установленный на Windows
- **PyInstaller** (pip install pyinstaller)
- Все файлы проекта в одной папке

## Файлы для сборки

Необходимые файлы:
- `punishment_stacker.py` - основной модуль
- `run_stacker.py` - точка входа для GUI
- `test_commands.txt` - тестовые команды
- `real_commands.txt` - реальные команды

## Результат

После сборки получите:
- `dist/MAJESTIC_Punishment_Stacker.exe` (~15-25 MB)
- Самодостаточное приложение для Windows
- Не требует установки Python на целевом компьютере

## Альтернативы для других ОС

### Linux:
```bash
pyinstaller --onefile run_stacker.py
```

### macOS:
```bash
pyinstaller --onefile --windowed run_stacker.py
```

## Решение проблем

### Если не находится tkinter:
```bash
# Windows
pip install tk

# Linux  
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

### Если большой размер .exe:
```bash
# Добавить исключения
pyinstaller --onefile --exclude-module matplotlib --exclude-module numpy run_stacker.py
```

### Если не запускается GUI:
- Проверьте, что используется `--windowed`
- Убедитесь, что tkinter доступен
- Попробуйте запустить без `--windowed` для отладки