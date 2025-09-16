#!/usr/bin/env python3
"""
🏰 MAJESTIC Punishment Stacker
Простой запуск стакера наказаний
by peep (discord: peepletmebleed)
"""

try:
    from punishment_stacker import PunishmentStackerGUI
    
    print("🏰 MAJESTIC Punishment Stacker - Запуск...")
    print("by peep (discord: peepletmebleed)")
    print("─" * 50)
    
    app = PunishmentStackerGUI()
    app.run()
    
except ImportError as e:
    print("❌ Ошибка импорта:", e)
    print("Убедитесь, что файл punishment_stacker.py находится в той же папке")
except Exception as e:
    print("❌ Ошибка запуска:", e)
    input("\nНажмите Enter для выхода...")