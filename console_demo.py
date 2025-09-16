#!/usr/bin/env python3
"""
🏰 MAJESTIC Punishment Stacker - Console Demo
Демонстрация работы без GUI для Replit
by peep (discord: peepletmebleed)
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from punishment_stacker import PunishmentStackerConfig, PunishmentProcessor

def demo_stacker():
    """Демонстрация работы стакера без GUI"""
    print("🏰 MAJESTIC Punishment Stacker - Console Demo")
    print("by peep (discord: peepletmebleed)")
    print("─" * 60)
    
    # Создаем конфигурацию и процессор
    config = PunishmentStackerConfig()
    processor = PunishmentProcessor(config)
    
    # Пример команд для демонстрации
    demo_commands = [
        "/ajail 123456 30 1.2.1 ПГО (01.01.2025) by Moderator1",
        "/ajail 123456 45 1.4 ПГО (01.01.2025) by Moderator2", 
        "/warn 123456 1.2.2 ПГО (02.01.2025) by Moderator1"
    ]
    
    print("📋 Исходные команды:")
    for i, cmd in enumerate(demo_commands, 1):
        print(f"  {i}. {cmd}")
    
    print("\n⚙️  Обработка...")
    
    # Обрабатываем команды
    results = processor.process_all_commands(demo_commands)
    
    print("\n✅ Результат стакинга:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result}")
    
    print("\n📊 Конфигурация стакера:")
    print(f"  • Максимум ajail: {config.max_ajail_duration} мин")
    print(f"  • Максимум warn: {config.max_warn_duration} мин")
    print(f"  • Делитель ban: {config.ban_duration_divider}")
    print(f"  • Warn = ajail: {config.warn_ajail_equivalent} мин")
    print(f"  • Тема: {config.theme}")
    
    print("\n🎯 Возможности приложения:")
    print("  • Автоматическая эскалация наказаний")
    print("  • Группировка по модераторам и датам")
    print("  • Поддержка кастомных формул")
    print("  • Лимиты для ПГО нарушений")
    print("  • Несколько тем оформления")
    print("  • Сохранение/загрузка конфигурации")
    
    print("\n💡 Для полного GUI запустите приложение в desktop окружении!")
    print("   python run_stacker.py")

if __name__ == "__main__":
    try:
        demo_stacker()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Проверьте наличие файла punishment_stacker.py")