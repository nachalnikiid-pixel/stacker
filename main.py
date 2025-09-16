#!/usr/bin/env python3
"""
🏰 MAJESTIC Punishment Stacker
Главный файл запуска
by peep (discord: peepletmebleed)
"""

import os
import sys

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from punishment_stacker import PunishmentStackerGUI
    
    print("🏰 MAJESTIC Punishment Stacker - Запуск...")
    print("by peep (discord: peepletmebleed)")
    print("─" * 50)
    
    # Для Replit - проверяем доступность GUI
    try:
        app = PunishmentStackerGUI()
        app.run()
    except Exception as gui_error:
        print("⚠️  GUI недоступен в текущей среде")
        print("Это приложение предназначено для запуска в desktop окружении")
        print(f"Ошибка: {gui_error}")
        
        # Показываем информацию о приложении
        print("\n📋 Информация о приложении:")
        print("- Приложение для стакинга наказаний игроков")
        print("- Поддерживает /ajail, /ban, /warn, /hardban")
        print("- Гибкая настройка параметров стакинга")
        print("- Тёмная тема интерфейса")
        print("- Автоматическая эскалация наказаний")
        
except ImportError as e:
    print("❌ Ошибка импорта:", e)
    print("Убедитесь, что файл punishment_stacker.py находится в той же папке")
except Exception as e:
    print("❌ Ошибка запуска:", e)
    
print("\nДля запуска GUI версии используйте desktop окружение")