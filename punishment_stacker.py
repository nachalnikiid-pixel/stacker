from __future__ import annotations
import json
import os
import re
from typing import Dict, List, Any, Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkFont


class PunishmentStackerConfig:
    """Класс для хранения и управления конфигурацией приложения"""
    
    def __init__(self):
        # Основные параметры стакинга
        self.max_ajail_duration = 90
        self.max_warn_duration = 120
        self.max_multi_warn_duration = 140
        self.ban_duration_divider = 30
        self.warn_ajail_equivalent = 100
        
        # Файлы по умолчанию
        self.default_input_file = "commands.txt"
        self.default_output_file = "results.txt"
        
        # Лимиты для различных нарушений
        self.pgo_limits = {
            "1.2.1 ПГО": {"ban": 30, "hardban": 30},
            "1.4 ПГО": {"ban": 30, "hardban": 30},
            "1.2.2 ПГО": {"ban": 15, "hardban": 15}
        }
        
        # Настройки логики стакинга
        self.enable_auto_escalation = True
        self.enable_pgo_limits = True
        self.enable_multi_reason_bonus = True
        self.escalation_formula = "linear"  # linear, exponential, custom
        self.reason_grouping_mode = "by_moderator"  # by_moderator, by_date, combined
        self.duplicate_reason_handling = "merge"  # merge, stack, keep_separate
        
        # Кастомные формулы
        self.custom_formulas = {
            "ajail_to_ban": "ajail_minutes / ban_duration_divider",
            "warn_threshold": "max_ajail_duration < total_minutes <= max_warn_duration",
            "multi_warn_threshold": "max_warn_duration < total_minutes <= max_multi_warn_duration"
        }
        
        # Настройки темы
        self.theme = "dark_red"
        self.themes = {
            "dark_red": {
                "bg": "#1a1a1a",
                "fg": "#ffffff",
                "select_bg": "#8B0000",
                "select_fg": "#ffffff",
                "button_bg": "#8B0000",
                "button_fg": "#ffffff",
                "entry_bg": "#2d2d2d",
                "entry_fg": "#ffffff",
                "frame_bg": "#252525",
                "accent": "#DC143C",
                "hover": "#A0002A"
            },
            "majestic": {
                "bg": "#0a0a0a",
                "fg": "#ffffff",
                "select_bg": "#4A0080",
                "select_fg": "#ffffff", 
                "button_bg": "#4A0080",
                "button_fg": "#ffffff",
                "entry_bg": "#1a1a1a",
                "entry_fg": "#ffffff",
                "frame_bg": "#151515",
                "accent": "#8A2BE2",
                "hover": "#6A1B9A"
            },
            "classic": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "button_bg": "#0078d4", 
                "button_fg": "#ffffff",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "frame_bg": "#e5e5e5",
                "accent": "#106ebe",
                "hover": "#005a9e"
            }
        }
    
    def save_to_file(self, filename: str):
        """Сохранение конфигурации в файл"""
        config_data = {
            "max_ajail_duration": self.max_ajail_duration,
            "max_warn_duration": self.max_warn_duration,
            "max_multi_warn_duration": self.max_multi_warn_duration,
            "ban_duration_divider": self.ban_duration_divider,
            "warn_ajail_equivalent": self.warn_ajail_equivalent,
            "default_input_file": self.default_input_file,
            "default_output_file": self.default_output_file,
            "pgo_limits": self.pgo_limits,
            "theme": self.theme
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str):
        """Загрузка конфигурации из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            return True
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return False
    
    def get_current_theme(self):
        """Получение текущей темы"""
        return self.themes.get(self.theme, self.themes["dark_red"])


class FormulaEvaluator:
    """Безопасный оценщик пользовательских формул"""
    
    def __init__(self):
        # Разрешенные операторы и функции
        self.allowed_ops = {
            '+', '-', '*', '/', '//', '%', '**', 
            '<', '>', '<=', '>=', '==', '!=',
            'and', 'or', 'not', 'min', 'max', 'round', 'int', 'float'
        }
    
    def safe_eval(self, formula: str, variables: dict) -> float:
        """Безопасная оценка формулы с заданными переменными"""
        try:
            # Простая проверка безопасности - только разрешенные символы и операции
            if any(char in formula for char in ['import', 'exec', 'eval', '__']):
                raise ValueError("Небезопасная формула")
            
            # Создаем локальное окружение с переменными и безопасными функциями
            local_vars = variables.copy()
            local_vars.update({
                'min': min, 'max': max, 'round': round, 'int': int, 'float': float
            })
            
            # Выполняем формулу
            result = eval(formula, {"__builtins__": {}}, local_vars)
            return float(result) if result is not None else 0.0
            
        except Exception as e:
            print(f"Ошибка в формуле '{formula}': {e}")
            return 0.0


class PunishmentProcessor:
    """Класс для обработки наказаний с гибкой логикой"""
    
    def __init__(self, config: PunishmentStackerConfig):
        self.config = config
        self.formula_evaluator = FormulaEvaluator()
    
    def parse_command(self, command_string: str) -> Dict[str, Any] | None:
        """Разбирает строку команды и возвращает словарь с информацией о наказании"""
        parts = command_string.split()

        if len(parts) < 5:
            print(f"Предупреждение: Некорректная команда: {command_string}")
            return None

        command_type = parts[0]
        static_id = parts[1]

        if command_type in ("/ajail", "/ban", "/hardban"):
            try:
                duration = int(parts[2])
            except ValueError:
                print(f"Предупреждение: Некорректная длительность в команде: {command_string}")
                return None
            reason_start_index = 3
        elif command_type == "/warn":
            duration = None
            reason_start_index = 2
        else:
            print(f"Предупреждение: Неизвестный тип команды: {command_string}")
            return None

        reason_parts = parts[reason_start_index:]

        try:
            by_index = reason_parts.index("by")
        except ValueError:
            print(f"Предупреждение: Отсутствует информация о модераторе в команде: {command_string}")
            return None

        reason = " ".join(reason_parts[:by_index])
        moderator_info = " ".join(reason_parts[by_index:])

        if not reason:
            print(f"Предупреждение: Отсутствует причина наказания в команде: {command_string}")
            return None

        date_match = re.search(r"\((.*?)\)", reason)
        date = date_match.group(1) if date_match else None
        reason = re.sub(r"\((.*?)\)", "", reason).strip()

        moderator_info = moderator_info.replace("by ", "", 1)

        return {
            "command_type": command_type,
            "static_id": static_id,
            "duration": duration,
            "reason": reason,
            "date": date,
            "moderator_info": moderator_info
        }

    def extract_date(self, item: str) -> str:
        """Извлекает дату из строки"""
        date_search = re.search(r'\((.*?)\)', item)
        return date_search.group(1) if date_search else ""

    def calculate_escalation(self, ajail_minutes: int, ban_days: int, hardban_days: int, 
                           punishment_reasons: Dict[str, int]) -> tuple[Optional[str], Optional[int]]:
        """Рассчитывает эскалацию наказания с учетом настроек"""
        
        # Если автоэскалация отключена, возвращаем исходное наказание
        if not self.config.enable_auto_escalation:
            if hardban_days > 0:
                return "/hardban", hardban_days
            elif ban_days > 0:
                return "/ban", ban_days  
            elif ajail_minutes > 0:
                return "/ajail", ajail_minutes
            else:
                return None, None
        
        total_minutes = ajail_minutes
        reason_count = len(punishment_reasons)
        different_reasons = reason_count > 1
        
        # Применяем бонус для множественных нарушений
        if self.config.enable_multi_reason_bonus and different_reasons:
            if self.config.escalation_formula == "exponential":
                total_minutes = round(total_minutes * (1.2 ** (reason_count - 1)))
            elif self.config.escalation_formula == "custom" and "multi_reason_bonus" in self.config.custom_formulas:
                vars_dict = {
                    "total_minutes": total_minutes,
                    "reason_count": reason_count,
                    "base_multiplier": 1.2
                }
                total_minutes = round(self.formula_evaluator.safe_eval(
                    self.config.custom_formulas["multi_reason_bonus"], vars_dict
                ))
        
        # Переменные для формул
        formula_vars = {
            "ajail_minutes": total_minutes,
            "ban_days": ban_days,
            "hardban_days": hardban_days,
            "total_minutes": total_minutes,
            "reason_count": reason_count,
            "different_reasons": different_reasons,
            "max_ajail_duration": self.config.max_ajail_duration,
            "max_warn_duration": self.config.max_warn_duration,
            "max_multi_warn_duration": self.config.max_multi_warn_duration,
            "ban_duration_divider": self.config.ban_duration_divider,
            "warn_ajail_equivalent": self.config.warn_ajail_equivalent
        }
        
        # Определение типа наказания
        if hardban_days > 0:
            final_command_type = "/hardban"
            if self.config.escalation_formula == "custom" and "hardban_conversion" in self.config.custom_formulas:
                final_duration = round(self.formula_evaluator.safe_eval(
                    self.config.custom_formulas["hardban_conversion"], formula_vars
                ))
            else:
                final_duration = round(hardban_days + (total_minutes / self.config.ban_duration_divider) + ban_days)
                
        elif ban_days > 0:
            final_command_type = "/ban"
            if self.config.escalation_formula == "custom" and "ban_conversion" in self.config.custom_formulas:
                final_duration = round(self.formula_evaluator.safe_eval(
                    self.config.custom_formulas["ban_conversion"], formula_vars
                ))
            else:
                final_duration = round(ban_days + (total_minutes / self.config.ban_duration_divider))
                
        elif (reason_count == 1 and "1.2.2 ПГО" in punishment_reasons and 
              self.config.max_ajail_duration < total_minutes <= self.config.max_warn_duration):
            return "/warn", 0
            
        elif (different_reasons and 
              self.config.max_warn_duration < total_minutes <= self.config.max_multi_warn_duration):
            return "/warn", 0
            
        elif (total_minutes > self.config.max_multi_warn_duration or 
              (reason_count == 1 and total_minutes > self.config.max_ajail_duration)):
            final_command_type = "/ban"
            if self.config.escalation_formula == "exponential":
                final_duration = round((total_minutes / self.config.ban_duration_divider) * 1.1)
            elif self.config.escalation_formula == "custom" and "ajail_to_ban" in self.config.custom_formulas:
                final_duration = round(self.formula_evaluator.safe_eval(
                    self.config.custom_formulas["ajail_to_ban"], formula_vars
                ))
            else:
                final_duration = round(total_minutes / self.config.ban_duration_divider)
                
        elif total_minutes > 0:
            return "/ajail", total_minutes
        else:
            return None, None
        
        # Применяем ПГО лимиты если включены
        if self.config.enable_pgo_limits and len(punishment_reasons) == 1:
            reason = list(punishment_reasons.keys())[0]
            if reason in self.config.pgo_limits:
                if final_command_type == "/ban":
                    final_duration = min(final_duration, self.config.pgo_limits[reason]["ban"])
                elif final_command_type == "/hardban":
                    final_duration = min(final_duration, self.config.pgo_limits[reason]["hardban"])
        
        return final_command_type, final_duration
    
    def group_reasons(self, moderator_reasons: Dict[str, List[str]]) -> str:
        """Группирует причины согласно выбранному режиму"""
        
        if self.config.reason_grouping_mode == "by_date":
            # Группировка по датам
            all_items = []
            for moderator, reasons in moderator_reasons.items():
                for item in reasons:
                    date = self.extract_date(item)
                    reason = item.split('(')[0].strip()
                    all_items.append((date, reason, moderator))
            
            all_items.sort(key=lambda x: x[0])  # Сортировка по дате
            
            date_groups: Dict[str, List[tuple]] = {}
            for date, reason, moderator in all_items:
                if date not in date_groups:
                    date_groups[date] = []
                date_groups[date].append((reason, moderator))
            
            reason_parts = []
            for date in sorted(date_groups.keys()):
                items = date_groups[date]
                if self.config.duplicate_reason_handling == "merge":
                    # Объединяем одинаковые причины
                    unique_reasons = {}
                    for reason, moderator in items:
                        if reason not in unique_reasons:
                            unique_reasons[reason] = []
                        unique_reasons[reason].append(moderator)
                    
                    for reason, moderators in unique_reasons.items():
                        mod_str = ", ".join(set(moderators))  # Уникальные модераторы
                        reason_parts.append(f"{reason} ({date}) by {mod_str}")
                else:
                    # Оставляем как есть
                    for reason, moderator in items:
                        reason_parts.append(f"{reason} ({date}) by {moderator}")
            
            return " ".join(reason_parts)
        
        elif self.config.reason_grouping_mode == "combined":
            # Комбинированная группировка
            all_reasons = []
            all_dates = set()
            all_moderators = set()
            
            for moderator, reasons in moderator_reasons.items():
                all_moderators.add(moderator)
                for item in reasons:
                    date = self.extract_date(item)
                    reason = item.split('(')[0].strip()
                    all_reasons.append(reason)
                    all_dates.add(date)
            
            if self.config.duplicate_reason_handling == "merge":
                unique_reasons = list(set(all_reasons))
            else:
                unique_reasons = all_reasons
            
            reason_str = " + ".join(unique_reasons)
            date_str = " ".join(f"({date})" for date in sorted(all_dates))
            mod_str = ", ".join(sorted(all_moderators))
            
            return f"{reason_str} {date_str} by {mod_str}"
        
        else:
            # По умолчанию: группировка по модераторам (существующая логика)
            reason_string = ""
            for moderator, reasons in moderator_reasons.items():
                reasons.sort(key=self.extract_date)
                collected_reasons: Dict[str, List[str]] = {}
                
                for item in reasons:
                    date = self.extract_date(item)
                    reason = item.split('(')[0].strip()
                    
                    if self.config.duplicate_reason_handling == "keep_separate":
                        # Каждая причина отдельно
                        key = f"{reason}_{date}"
                    else:
                        # Группируем одинаковые причины
                        key = reason
                    
                    if key not in collected_reasons:
                        collected_reasons[key] = []
                    collected_reasons[key].append(date)

                moderator_str = ""
                for reason_key, dates in collected_reasons.items():
                    if "_" in reason_key and self.config.duplicate_reason_handling == "keep_separate":
                        reason = reason_key.split("_")[0]
                        dates_str = f"({dates[0]})"
                    else:
                        reason = reason_key
                        if self.config.duplicate_reason_handling == "merge":
                            dates_str = " ".join(f"({date})" for date in sorted(set(dates)))
                        else:
                            dates_str = " ".join(f"({date})" for date in sorted(dates))
                    
                    moderator_str += f"{reason} {dates_str} "

                reason_string += f"{moderator_str}by {moderator} "

            return reason_string.strip()
    
    def process_player_commands(self, command_strings: List[str]) -> str | None:
        """Обрабатывает список команд для одного игрока с гибкой логикой"""
        parsed_commands = [self.parse_command(cmd) for cmd in command_strings]
        parsed_commands = [cmd for cmd in parsed_commands if cmd]

        if not parsed_commands:
            return None

        static_id = parsed_commands[0]["static_id"]
        total_ajail_minutes = 0
        ban_days = 0
        hardban_days = 0
        punishment_reasons: Dict[str, int] = {}
        moderator_reasons: Dict[str, List[str]] = {}

        # Обработка всех команд
        for cmd in parsed_commands:
            if cmd["command_type"] == "/ajail":
                total_ajail_minutes += cmd["duration"]
            elif cmd["command_type"] == "/ban":
                ban_days += cmd["duration"]
            elif cmd["command_type"] == "/warn":
                total_ajail_minutes += self.config.warn_ajail_equivalent
            elif cmd["command_type"] == "/hardban":
                hardban_days += cmd["duration"]

            moderator = cmd['moderator_info']
            reasons = cmd["reason"].split(" + ")
            
            for reason in reasons:
                punishment_reasons[reason] = punishment_reasons.get(reason, 0) + 1
                
                if moderator not in moderator_reasons:
                    moderator_reasons[moderator] = []
                moderator_reasons[moderator].append(f"{reason} ({cmd['date']})")

        # Вычисляем финальное наказание с учетом настроек
        final_command_type, final_duration = self.calculate_escalation(
            total_ajail_minutes, ban_days, hardban_days, punishment_reasons
        )
        
        if not final_command_type:
            return None

        # Формируем строку причин с учетом режима группировки
        reason_string = self.group_reasons(moderator_reasons)

        if final_command_type == "/warn":
            return f"/warn {static_id} {reason_string}"
        else:
            return f"{final_command_type} {static_id} {final_duration} {reason_string}"

    def process_all_commands(self, all_commands: List[str]) -> List[str]:
        """Обрабатывает все команды, группируя их по static_id"""
        grouped_commands: Dict[str, List[str]] = {}
        
        for command in all_commands:
            try:
                static_id = command.split()[1]
                if static_id not in grouped_commands:
                    grouped_commands[static_id] = []
                grouped_commands[static_id].append(command)
            except IndexError:
                print(f"Ошибка обработки команды: {command}")
                continue

        results: List[str] = []
        for static_id, commands in grouped_commands.items():
            if len(commands) > 1:
                result = self.process_player_commands(commands)
                if result:
                    results.append(result)
            else:
                results.append(commands[0])
                
        return results


class PunishmentStackerGUI:
    """Главный класс GUI приложения"""
    
    def __init__(self):
        self.config = PunishmentStackerConfig()
        self.processor = PunishmentProcessor(self.config)
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.apply_theme()
        
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("🏰 Majestic Punishment Stacker by peep")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Иконка (если есть)
        try:
            self.root.iconbitmap("majestic.ico")
        except:
            pass
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Заголовок с логотипом
        header_frame = tk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = tk.Label(header_frame, text="🏰 MAJESTIC", font=("Arial", 16, "bold"))
        title_label.pack(side="left")
        
        subtitle_label = tk.Label(header_frame, text="Punishment Stacker", font=("Arial", 12))
        subtitle_label.pack(side="left", padx=(10, 0))
        
        author_label = tk.Label(header_frame, text="by peep (discord: peepletmebleed)", 
                               font=("Arial", 9, "italic"))
        author_label.pack(side="right")
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Вкладка основных функций
        self.main_tab = tk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="📋 Основное")
        
        # Вкладка настроек
        self.settings_tab = tk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Настройки")
        
        # Вкладка предпросмотра
        self.preview_tab = tk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="👁️ Предпросмотр")
        
        # Вкладка продвинутой логики
        self.logic_tab = tk.Frame(self.notebook)
        self.notebook.add(self.logic_tab, text="🧠 Логика стакинга")
        
        self.create_main_tab()
        self.create_settings_tab()
        self.create_logic_tab()
        self.create_preview_tab()
    
    def create_main_tab(self):
        """Создание основной вкладки"""
        # Файлы
        files_frame = tk.LabelFrame(self.main_tab, text="📁 Файлы", font=("Arial", 10, "bold"))
        files_frame.pack(fill="x", padx=10, pady=5)
        
        # Input файл
        tk.Label(files_frame, text="Файл с командами:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.input_file_var = tk.StringVar(value=self.config.default_input_file)
        self.input_entry = tk.Entry(files_frame, textvariable=self.input_file_var, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Button(files_frame, text="📂 Обзор", command=self.browse_input_file, width=8).grid(row=0, column=2, padx=5, pady=2)
        
        # Output файл
        tk.Label(files_frame, text="Файл результатов:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.output_file_var = tk.StringVar(value=self.config.default_output_file)
        self.output_entry = tk.Entry(files_frame, textvariable=self.output_file_var, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Button(files_frame, text="💾 Выбрать", command=self.browse_output_file, width=8).grid(row=1, column=2, padx=5, pady=2)
        
        # Кнопки действий
        action_frame = tk.Frame(self.main_tab)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(action_frame, text="🔄 Предпросмотр", command=self.preview_processing, 
                 font=("Arial", 10, "bold"), height=2).pack(side="left", padx=5, fill="x", expand=True)
        
        tk.Button(action_frame, text="⚡ СТАКНУТЬ", command=self.process_commands,
                 font=("Arial", 12, "bold"), height=2).pack(side="left", padx=5, fill="x", expand=True)
        
        # Статистика
        stats_frame = tk.LabelFrame(self.main_tab, text="📊 Статистика", font=("Arial", 10, "bold"))
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, wrap="word")
        stats_scrollbar = tk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        stats_scrollbar.pack(side="right", fill="y", pady=5)
    
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        # Основные параметры
        params_frame = tk.LabelFrame(self.settings_tab, text="🎛️ Параметры стакинга", font=("Arial", 10, "bold"))
        params_frame.pack(fill="x", padx=10, pady=5)
        
        # Создание полей для настройки
        self.param_vars = {}
        params = [
            ("max_ajail_duration", "Макс. длительность AJail (мин):", 90),
            ("max_warn_duration", "Макс. длительность для Warn (мин):", 120),
            ("max_multi_warn_duration", "Макс. длительность мульти-Warn (мин):", 140),
            ("ban_duration_divider", "Делитель для конвертации в Ban:", 30),
            ("warn_ajail_equivalent", "Warn как AJail минуты:", 100)
        ]
        
        for i, (param, label, default) in enumerate(params):
            tk.Label(params_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.IntVar(value=getattr(self.config, param))
            self.param_vars[param] = var
            entry = tk.Entry(params_frame, textvariable=var, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
        
        # Лимиты для нарушений
        limits_frame = tk.LabelFrame(self.settings_tab, text="⚖️ Лимиты наказаний", font=("Arial", 10, "bold"))
        limits_frame.pack(fill="x", padx=10, pady=5)
        
        self.limits_vars = {}
        row = 0
        for violation, limits in self.config.pgo_limits.items():
            tk.Label(limits_frame, text=f"{violation}:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            tk.Label(limits_frame, text="Ban лимит:").grid(row=row, column=1, padx=5, pady=2)
            ban_var = tk.IntVar(value=limits["ban"])
            self.limits_vars[f"{violation}_ban"] = ban_var
            tk.Entry(limits_frame, textvariable=ban_var, width=8).grid(row=row, column=2, padx=2, pady=2)
            
            tk.Label(limits_frame, text="HardBan лимит:").grid(row=row, column=3, padx=5, pady=2)
            hardban_var = tk.IntVar(value=limits["hardban"])
            self.limits_vars[f"{violation}_hardban"] = hardban_var
            tk.Entry(limits_frame, textvariable=hardban_var, width=8).grid(row=row, column=4, padx=2, pady=2)
            
            row += 1
        
        # Темы
        theme_frame = tk.LabelFrame(self.settings_tab, text="🎨 Оформление", font=("Arial", 10, "bold"))
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(theme_frame, text="Тема:").pack(side="left", padx=5)
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                  values=list(self.config.themes.keys()), width=15)
        theme_combo.pack(side="left", padx=5)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme())
        
        # Кнопки управления конфигурацией
        config_frame = tk.Frame(self.settings_tab)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(config_frame, text="💾 Сохранить конфиг", 
                 command=self.save_config).pack(side="left", padx=5)
        tk.Button(config_frame, text="📂 Загрузить конфиг", 
                 command=self.load_config).pack(side="left", padx=5)
        tk.Button(config_frame, text="🔄 Применить настройки", 
                 command=self.apply_settings).pack(side="left", padx=5)
        tk.Button(config_frame, text="↩️ Сбросить", 
                 command=self.reset_settings).pack(side="left", padx=5)
    
    def create_logic_tab(self):
        """Создание вкладки настройки логики стакинга"""
        # Основные переключатели логики
        logic_frame = tk.LabelFrame(self.logic_tab, text="🔧 Алгоритмы стакинга", font=("Arial", 10, "bold"))
        logic_frame.pack(fill="x", padx=10, pady=5)
        
        # Создание переключателей
        self.logic_vars = {}
        
        logic_options = [
            ("enable_auto_escalation", "Автоматическая эскалация наказаний", True),
            ("enable_pgo_limits", "Применять лимиты для ПГО нарушений", True),
            ("enable_multi_reason_bonus", "Бонус для множественных нарушений", True)
        ]
        
        for i, (option, label, default) in enumerate(logic_options):
            var = tk.BooleanVar(value=getattr(self.config, option, default))
            self.logic_vars[option] = var
            tk.Checkbutton(logic_frame, text=label, variable=var).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        
        # Формулы эскалации
        formula_frame = tk.LabelFrame(self.logic_tab, text="📊 Формулы конвертации", font=("Arial", 10, "bold"))
        formula_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(formula_frame, text="Формула эскалации:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.escalation_var = tk.StringVar(value=self.config.escalation_formula)
        escalation_combo = ttk.Combobox(formula_frame, textvariable=self.escalation_var, 
                                       values=["linear", "exponential", "custom"], width=15)
        escalation_combo.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(formula_frame, text="Группировка причин:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.grouping_var = tk.StringVar(value=self.config.reason_grouping_mode)
        grouping_combo = ttk.Combobox(formula_frame, textvariable=self.grouping_var,
                                     values=["by_moderator", "by_date", "combined"], width=15)
        grouping_combo.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(formula_frame, text="Дублированные причины:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.duplicate_var = tk.StringVar(value=self.config.duplicate_reason_handling)
        duplicate_combo = ttk.Combobox(formula_frame, textvariable=self.duplicate_var,
                                      values=["merge", "stack", "keep_separate"], width=15)
        duplicate_combo.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # Пользовательские формулы
        custom_frame = tk.LabelFrame(self.logic_tab, text="🧮 Пользовательские формулы", font=("Arial", 10, "bold"))
        custom_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание текстового поля для редактирования формул
        tk.Label(custom_frame, text="Редактировать JSON формулы:").pack(anchor="w", padx=5, pady=2)
        
        self.formula_text = tk.Text(custom_frame, height=10, wrap="word", font=("Consolas", 9))
        formula_scrollbar = tk.Scrollbar(custom_frame, orient="vertical", command=self.formula_text.yview)
        self.formula_text.configure(yscrollcommand=formula_scrollbar.set)
        
        self.formula_text.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        formula_scrollbar.pack(side="right", fill="y", pady=5)
        
        # Заполнение начальными формулами
        formula_json = json.dumps(self.config.custom_formulas, indent=2, ensure_ascii=False)
        self.formula_text.insert(tk.END, formula_json)
        
        # Кнопки управления формулами
        formula_buttons = tk.Frame(custom_frame)
        formula_buttons.pack(fill="x", padx=5, pady=5)
        
        tk.Button(formula_buttons, text="✅ Применить формулы", 
                 command=self.apply_custom_formulas).pack(side="left", padx=2)
        tk.Button(formula_buttons, text="🔄 Сбросить формулы", 
                 command=self.reset_formulas).pack(side="left", padx=2)
        tk.Button(formula_buttons, text="📋 Примеры формул", 
                 command=self.show_formula_examples).pack(side="left", padx=2)
    
    def create_preview_tab(self):
        """Создание вкладки предпросмотра"""
        # Текстовое поле для предпросмотра
        self.preview_text = tk.Text(self.preview_tab, wrap="word", font=("Consolas", 10))
        preview_scrollbar_y = tk.Scrollbar(self.preview_tab, orient="vertical", command=self.preview_text.yview)
        preview_scrollbar_x = tk.Scrollbar(self.preview_tab, orient="horizontal", command=self.preview_text.xview)
        
        self.preview_text.configure(yscrollcommand=preview_scrollbar_y.set, xscrollcommand=preview_scrollbar_x.set)
        
        self.preview_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        preview_scrollbar_y.pack(side="right", fill="y", pady=10)
        preview_scrollbar_x.pack(side="bottom", fill="x", padx=10)
    
    def apply_theme(self):
        """Применение выбранной темы"""
        theme = self.config.get_current_theme()
        
        def style_widget(widget, **kwargs):
            try:
                for key, value in kwargs.items():
                    widget.configure(**{key: value})
            except:
                pass
        
        # Стилизация главного окна
        self.root.configure(bg=theme["bg"])
        
        # Настройка стилей для ttk виджетов
        style = ttk.Style()
        style.theme_use('clam')  # Базовая тема для кастомизации
        
        # Стилизация Notebook
        style.configure('TNotebook', background=theme["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=theme["frame_bg"], 
                       foreground=theme["fg"],
                       padding=[20, 8],
                       borderwidth=1)
        style.map('TNotebook.Tab',
                 background=[('selected', theme["accent"]),
                           ('active', theme["hover"])],
                 foreground=[('selected', theme["fg"])])
        
        # Стилизация Combobox
        style.configure('TCombobox',
                       fieldbackground=theme["entry_bg"],
                       background=theme["entry_bg"],
                       foreground=theme["entry_fg"],
                       borderwidth=1,
                       relief='solid')
        style.map('TCombobox',
                 fieldbackground=[('readonly', theme["entry_bg"])],
                 selectbackground=[('readonly', theme["select_bg"])])
        
        # Рекурсивная стилизация всех виджетов
        def apply_to_children(parent):
            for child in parent.winfo_children():
                widget_class = child.winfo_class()
                
                if widget_class == "Frame":
                    style_widget(child, bg=theme["bg"])
                elif widget_class == "Label":
                    style_widget(child, bg=theme["bg"], fg=theme["fg"])
                elif widget_class == "Button":
                    style_widget(child, bg=theme["button_bg"], fg=theme["button_fg"], 
                               activebackground=theme["hover"], activeforeground=theme["button_fg"])
                elif widget_class == "Entry":
                    style_widget(child, bg=theme["entry_bg"], fg=theme["entry_fg"], 
                               insertbackground=theme["fg"])
                elif widget_class == "Text":
                    style_widget(child, bg=theme["entry_bg"], fg=theme["entry_fg"], 
                               insertbackground=theme["fg"])
                elif widget_class == "Labelframe":
                    style_widget(child, bg=theme["bg"], fg=theme["accent"])
                
                apply_to_children(child)
        
        apply_to_children(self.root)
    
    def change_theme(self):
        """Смена темы"""
        self.config.theme = self.theme_var.get()
        self.apply_theme()
    
    def browse_input_file(self):
        """Выбор входного файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл с командами",
            filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )
        if filename:
            self.input_file_var.set(filename)
    
    def browse_output_file(self):
        """Выбор выходного файла"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить результаты как",
            defaultextension=".txt",
            filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )
        if filename:
            self.output_file_var.set(filename)
    
    def apply_settings(self):
        """Применение настроек"""
        # Обновление основных параметров
        for param, var in self.param_vars.items():
            setattr(self.config, param, var.get())
        
        # Обновление лимитов
        for key, var in self.limits_vars.items():
            parts = key.rsplit("_", 1)
            if len(parts) == 2:
                violation, limit_type = parts
                if violation not in self.config.pgo_limits:
                    self.config.pgo_limits[violation] = {"ban": 30, "hardban": 30}
                self.config.pgo_limits[violation][limit_type] = var.get()
        
        # Обновление настроек логики (если существуют)
        if hasattr(self, 'logic_vars'):
            for param, var in self.logic_vars.items():
                setattr(self.config, param, var.get())
        
        if hasattr(self, 'escalation_var'):
            self.config.escalation_formula = self.escalation_var.get()
        if hasattr(self, 'grouping_var'):
            self.config.reason_grouping_mode = self.grouping_var.get()
        if hasattr(self, 'duplicate_var'):
            self.config.duplicate_reason_handling = self.duplicate_var.get()
        
        # Обновление темы
        self.config.theme = self.theme_var.get()
        
        # Пересоздание процессора с новой конфигурацией
        self.processor = PunishmentProcessor(self.config)
        messagebox.showinfo("Успех", "Настройки применены!")
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        self.config = PunishmentStackerConfig()
        
        # Обновление переменных интерфейса
        for param, var in self.param_vars.items():
            var.set(getattr(self.config, param))
        
        row = 0
        for violation, limits in self.config.pgo_limits.items():
            if f"{violation}_ban" in self.limits_vars:
                self.limits_vars[f"{violation}_ban"].set(limits["ban"])
            if f"{violation}_hardban" in self.limits_vars:
                self.limits_vars[f"{violation}_hardban"].set(limits["hardban"])
        
        self.theme_var.set(self.config.theme)
        self.apply_theme()
        messagebox.showinfo("Успех", "Настройки сброшены!")
    
    def apply_custom_formulas(self):
        """Применение пользовательских формул"""
        try:
            formula_text = self.formula_text.get(1.0, tk.END).strip()
            new_formulas = json.loads(formula_text)
            
            # Валидация формул
            required_keys = ["ajail_to_ban", "warn_threshold", "multi_warn_threshold"]
            for key in required_keys:
                if key not in new_formulas:
                    messagebox.showerror("Ошибка", f"Отсутствует обязательная формула: {key}")
                    return
            
            self.config.custom_formulas = new_formulas
            self.processor = PunishmentProcessor(self.config)
            messagebox.showinfo("Успех", "Пользовательские формулы применены!")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Некорректный JSON формат: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить формулы: {e}")
    
    def reset_formulas(self):
        """Сброс формул к значениям по умолчанию"""
        default_formulas = {
            "ajail_to_ban": "ajail_minutes / ban_duration_divider",
            "warn_threshold": "max_ajail_duration < total_minutes <= max_warn_duration",
            "multi_warn_threshold": "max_warn_duration < total_minutes <= max_multi_warn_duration",
            "pgo_ban_limit": "min(calculated_duration, pgo_limits[reason]['ban'])",
            "pgo_hardban_limit": "min(calculated_duration, pgo_limits[reason]['hardban'])"
        }
        
        self.config.custom_formulas = default_formulas
        self.formula_text.delete(1.0, tk.END)
        formula_json = json.dumps(default_formulas, indent=2, ensure_ascii=False)
        self.formula_text.insert(tk.END, formula_json)
        messagebox.showinfo("Успех", "Формулы сброшены к значениям по умолчанию!")
    
    def show_formula_examples(self):
        """Показать примеры формул"""
        examples_window = tk.Toplevel(self.root)
        examples_window.title("📋 Примеры формул")
        examples_window.geometry("600x400")
        
        # Применение темы к новому окну
        theme = self.config.get_current_theme()
        examples_window.configure(bg=theme["bg"])
        
        examples_text = tk.Text(examples_window, wrap="word", font=("Consolas", 10),
                               bg=theme["entry_bg"], fg=theme["entry_fg"])
        scrollbar = tk.Scrollbar(examples_window, orient="vertical", command=examples_text.yview)
        examples_text.configure(yscrollcommand=scrollbar.set)
        
        examples = '''
📋 ПРИМЕРЫ ПОЛЬЗОВАТЕЛЬСКИХ ФОРМУЛ

🔧 Базовые формулы:
{
  "ajail_to_ban": "ajail_minutes / ban_duration_divider",
  "warn_threshold": "max_ajail_duration < total_minutes <= max_warn_duration",
  "multi_warn_threshold": "max_warn_duration < total_minutes <= max_multi_warn_duration"
}

🎯 Продвинутые формулы:
{
  "exponential_escalation": "ajail_minutes * (1.5 ** escalation_level)",
  "time_based_bonus": "base_duration + (days_since_last * 0.1)",
  "severity_multiplier": "base_duration * severity_weights[reason_category]"
}

📊 Условные формулы:
{
  "smart_conversion": "ajail_minutes / 30 if reason_count > 3 else ajail_minutes / 20",
  "moderator_bonus": "base_duration * 1.2 if moderator_count > 2 else base_duration",
  "weekend_penalty": "base_duration * 1.5 if is_weekend else base_duration"
}

⚠️ Доступные переменные:
- ajail_minutes, ban_days, hardban_days
- total_minutes, reason_count, moderator_count
- max_ajail_duration, max_warn_duration, max_multi_warn_duration
- ban_duration_divider, warn_ajail_equivalent
- punishment_reasons, moderator_reasons

💡 Операторы: +, -, *, /, //, %, **, <, >, <=, >=, ==, !=, and, or, not
'''
        
        examples_text.insert(tk.END, examples)
        examples_text.configure(state="disabled")
        
        examples_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def save_config(self):
        """Сохранение конфигурации"""
        self.apply_settings()  # Применяем текущие настройки
        
        filename = filedialog.asksaveasfilename(
            title="Сохранить конфигурацию",
            defaultextension=".json",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
        )
        if filename:
            self.config.save_to_file(filename)
            messagebox.showinfo("Успех", f"Конфигурация сохранена в {filename}")
    
    def load_config(self):
        """Загрузка конфигурации"""
        filename = filedialog.askopenfilename(
            title="Загрузить конфигурацию",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
        )
        if filename and self.config.load_from_file(filename):
            # Обновление интерфейса
            self.input_file_var.set(self.config.default_input_file)
            self.output_file_var.set(self.config.default_output_file)
            
            # Обновление переменных настроек
            for param, var in self.param_vars.items():
                if hasattr(self.config, param):
                    var.set(getattr(self.config, param))
            
            self.theme_var.set(self.config.theme)
            self.apply_theme()
            self.processor = PunishmentProcessor(self.config)
            messagebox.showinfo("Успех", f"Конфигурация загружена из {filename}")
        elif filename:
            messagebox.showerror("Ошибка", "Не удалось загрузить конфигурацию")
    
    def read_commands_from_file(self, filename: str) -> List[str]:
        """Чтение команд из файла"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                commands = [line.strip() for line in f if line.strip()]
            return commands
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл '{filename}' не найден")
            return []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка чтения файла: {e}")
            return []
    
    def preview_processing(self):
        """Предпросмотр обработки команд"""
        input_file = self.input_file_var.get()
        if not os.path.exists(input_file):
            messagebox.showerror("Ошибка", "Файл с командами не найден")
            return
        
        try:
            commands = self.read_commands_from_file(input_file)
            if not commands:
                messagebox.showwarning("Предупреждение", "Файл с командами пуст")
                return
            
            results = self.processor.process_all_commands(commands)
            
            # Отображение в предпросмотре
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"📋 ПРЕДПРОСМОТР ОБРАБОТКИ\n")
            self.preview_text.insert(tk.END, f"═" * 50 + "\n\n")
            
            self.preview_text.insert(tk.END, f"📥 Исходных команд: {len(commands)}\n")
            self.preview_text.insert(tk.END, f"📤 Результирующих команд: {len(results)}\n\n")
            
            self.preview_text.insert(tk.END, "🔧 ОБРАБОТАННЫЕ КОМАНДЫ:\n")
            self.preview_text.insert(tk.END, "─" * 30 + "\n")
            
            for i, result in enumerate(results, 1):
                self.preview_text.insert(tk.END, f"{i:2d}. {result}\n")
            
            # Переключение на вкладку предпросмотра
            self.notebook.select(self.preview_tab)
            
            # Обновление статистики
            self.update_statistics(commands, results)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при предпросмотре: {e}")
    
    def process_commands(self):
        """Обработка команд и сохранение результатов"""
        input_file = self.input_file_var.get()
        output_file = self.output_file_var.get()
        
        if not os.path.exists(input_file):
            messagebox.showerror("Ошибка", "Файл с командами не найден")
            return
        
        if not output_file:
            messagebox.showerror("Ошибка", "Не указан файл для сохранения результатов")
            return
        
        try:
            commands = self.read_commands_from_file(input_file)
            if not commands:
                messagebox.showwarning("Предупреждение", "Файл с командами пуст")
                return
            
            results = self.processor.process_all_commands(commands)
            
            # Сохранение результатов
            with open(output_file, "w", encoding="utf-8") as f:
                for result in results:
                    f.write(result + "\n")
            
            self.update_statistics(commands, results)
            
            messagebox.showinfo("Успех", 
                              f"✅ Команды обработаны успешно!\n\n"
                              f"📥 Обработано команд: {len(commands)}\n"
                              f"📤 Создано команд: {len(results)}\n"
                              f"💾 Результаты сохранены в: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при обработке: {e}")
    
    def update_statistics(self, original_commands: List[str], processed_commands: List[str]):
        """Обновление статистики обработки"""
        self.stats_text.delete(1.0, tk.END)
        
        # Подсчет статистики
        command_types_orig = {}
        command_types_proc = {}
        
        for cmd in original_commands:
            cmd_type = cmd.split()[0] if cmd.split() else "unknown"
            command_types_orig[cmd_type] = command_types_orig.get(cmd_type, 0) + 1
        
        for cmd in processed_commands:
            cmd_type = cmd.split()[0] if cmd.split() else "unknown"
            command_types_proc[cmd_type] = command_types_proc.get(cmd_type, 0) + 1
        
        # Отображение статистики
        stats_text = f"📊 СТАТИСТИКА ОБРАБОТКИ\n"
        stats_text += f"═" * 40 + "\n\n"
        
        stats_text += f"📥 Исходные команды ({len(original_commands)}):\n"
        for cmd_type, count in sorted(command_types_orig.items()):
            stats_text += f"  {cmd_type}: {count}\n"
        
        stats_text += f"\n📤 Результирующие команды ({len(processed_commands)}):\n"
        for cmd_type, count in sorted(command_types_proc.items()):
            stats_text += f"  {cmd_type}: {count}\n"
        
        reduction = len(original_commands) - len(processed_commands)
        if reduction > 0:
            stats_text += f"\n🎯 Сокращение: {reduction} команд(-ы)\n"
            stats_text += f"📈 Эффективность: {reduction/len(original_commands)*100:.1f}%"
        
        self.stats_text.insert(tk.END, stats_text)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = PunishmentStackerGUI()
    app.run()