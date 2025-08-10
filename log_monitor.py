#!/usr/bin/env python3
"""
Скрипт для мониторинга логов Todo App
"""
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re

class LogMonitor:
    """Монитор логов приложения"""
    
    def __init__(self, log_dir: str = "logs", log_pattern: str = "*.log"):
        self.log_dir = Path(log_dir)
        self.log_pattern = log_pattern
        self.log_files = []
        self.stats = {
            "total_entries": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "debug_count": 0,
            "last_check": None,
            "new_entries": 0
        }
        
        # Создаем папку для логов если её нет
        self.log_dir.mkdir(exist_ok=True)
    
    def scan_log_files(self):
        """Сканирование файлов логов"""
        self.log_files = list(self.log_dir.glob(self.log_pattern))
        print(f"📁 Найдено {len(self.log_files)} файлов логов в {self.log_dir}")
        
        for log_file in self.log_files:
            print(f"   - {log_file.name}")
    
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """Парсинг строки лога"""
        # Базовый парсер для стандартных логов
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)'
        level_pattern = r'(ERROR|WARNING|INFO|DEBUG)'
        message_pattern = r'(.*)'
        
        full_pattern = f"{timestamp_pattern}.*{level_pattern}.*{message_pattern}"
        match = re.match(full_pattern, line.strip())
        
        if match:
            timestamp_str, level, message = match.groups()
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now()
            
            return {
                "timestamp": timestamp,
                "level": level,
                "message": message.strip(),
                "raw_line": line.strip()
            }
        
        return {
            "timestamp": datetime.now(),
            "level": "UNKNOWN",
            "message": line.strip(),
            "raw_line": line.strip()
        }
    
    def analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Анализ файла логов"""
        file_stats = {
            "filename": log_file.name,
            "size": log_file.stat().st_size,
            "entries": 0,
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "debug": 0,
            "last_modified": datetime.fromtimestamp(log_file.stat().st_mtime),
            "recent_entries": []
        }
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            file_stats["entries"] = len(lines)
            
            # Анализируем последние 100 строк
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            for line in recent_lines:
                if line.strip():
                    log_entry = self.parse_log_line(line)
                    
                    # Подсчитываем уровни
                    if log_entry["level"] == "ERROR":
                        file_stats["errors"] += 1
                        self.stats["error_count"] += 1
                    elif log_entry["level"] == "WARNING":
                        file_stats["warnings"] += 1
                        self.stats["warning_count"] += 1
                    elif log_entry["level"] == "INFO":
                        file_stats["info"] += 1
                        self.stats["info_count"] += 1
                    elif log_entry["level"] == "DEBUG":
                        file_stats["debug"] += 1
                        self.stats["debug_count"] += 1
                    
                    # Добавляем в недавние записи
                    if len(file_stats["recent_entries"]) < 10:
                        file_stats["recent_entries"].append(log_entry)
                    
                    self.stats["total_entries"] += 1
            
        except Exception as e:
            print(f"❌ Ошибка при чтении файла {log_file}: {e}")
        
        return file_stats
    
    def monitor_logs(self, interval: int = 30):
        """Мониторинг логов в реальном времени"""
        print(f"🔍 Запуск мониторинга логов (интервал: {interval} сек)")
        print("Нажмите Ctrl+C для остановки")
        
        try:
            while True:
                self.scan_log_files()
                
                print(f"\n📊 Статистика логов - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
                
                total_errors = 0
                total_warnings = 0
                
                for log_file in self.log_files:
                    file_stats = self.analyze_log_file(log_file)
                    
                    print(f"\n📄 {file_stats['filename']}")
                    print(f"   Размер: {file_stats['size']} байт")
                    print(f"   Записей: {file_stats['entries']}")
                    print(f"   Ошибки: {file_stats['errors']}")
                    print(f"   Предупреждения: {file_stats['warnings']}")
                    print(f"   Информация: {file_stats['info']}")
                    print(f"   Отладка: {file_stats['debug']}")
                    print(f"   Последнее изменение: {file_stats['last_modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    total_errors += file_stats['errors']
                    total_warnings += file_stats['warnings']
                    
                    # Показываем недавние записи
                    if file_stats['recent_entries']:
                        print("   Последние записи:")
                        for entry in file_stats['recent_entries'][-3:]:  # Последние 3
                            level_icon = {
                                "ERROR": "❌",
                                "WARNING": "⚠️",
                                "INFO": "ℹ️",
                                "DEBUG": "🔍"
                            }.get(entry["level"], "❓")
                            
                            print(f"     {level_icon} {entry['timestamp'].strftime('%H:%M:%S')} [{entry['level']}] {entry['message'][:80]}")
                
                print(f"\n📈 Общая статистика:")
                print(f"   Всего записей: {self.stats['total_entries']}")
                print(f"   Всего ошибок: {total_errors}")
                print(f"   Всего предупреждений: {total_warnings}")
                
                # Проверяем критические ошибки
                if total_errors > 0:
                    print(f"🚨 ВНИМАНИЕ: Обнаружено {total_errors} ошибок!")
                
                if total_warnings > 0:
                    print(f"⚠️  Предупреждений: {total_warnings}")
                
                self.stats["last_check"] = datetime.now()
                
                print(f"\n⏰ Следующая проверка через {interval} секунд...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Мониторинг остановлен пользователем")
    
    def search_logs(self, query: str, level: str = None, hours: int = 24):
        """Поиск в логах"""
        print(f"🔍 Поиск в логах: '{query}'")
        if level:
            print(f"   Уровень: {level}")
        print(f"   Временной диапазон: последние {hours} часов")
        print("="*60)
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        found_entries = []
        
        for log_file in self.log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            log_entry = self.parse_log_line(line)
                            
                            # Проверяем временной диапазон
                            if log_entry["timestamp"] < cutoff_time:
                                continue
                            
                            # Проверяем уровень
                            if level and log_entry["level"] != level:
                                continue
                            
                            # Проверяем поисковый запрос
                            if query.lower() in log_entry["message"].lower():
                                found_entries.append({
                                    "file": log_file.name,
                                    "line": line_num,
                                    "entry": log_entry
                                })
                                
                                # Показываем найденные записи
                                level_icon = {
                                    "ERROR": "❌",
                                    "WARNING": "⚠️",
                                    "INFO": "ℹ️",
                                    "DEBUG": "🔍"
                                }.get(log_entry["level"], "❓")
                                
                                print(f"{level_icon} [{log_entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] "
                                      f"[{log_entry['level']}] {log_entry['message']}")
                                print(f"   Файл: {log_file.name}:{line_num}")
                                print()
                                
            except Exception as e:
                print(f"❌ Ошибка при чтении файла {log_file}: {e}")
        
        print(f"🔍 Найдено {len(found_entries)} записей")
        return found_entries
    
    def export_logs(self, filename: str = None, hours: int = 24):
        """Экспорт логов в JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_export_{timestamp}.json"
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        export_data = {
            "export_time": datetime.now().isoformat(),
            "time_range_hours": hours,
            "cutoff_time": cutoff_time.isoformat(),
            "files": []
        }
        
        for log_file in self.log_files:
            file_data = {
                "filename": log_file.name,
                "entries": []
            }
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            log_entry = self.parse_log_line(line)
                            
                            if log_entry["timestamp"] >= cutoff_time:
                                file_data["entries"].append({
                                    "timestamp": log_entry["timestamp"].isoformat(),
                                    "level": log_entry["level"],
                                    "message": log_entry["message"]
                                })
                
                export_data["files"].append(file_data)
                
            except Exception as e:
                print(f"❌ Ошибка при экспорте файла {log_file}: {e}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Логи экспортированы в {filename}")
        return filename


def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Монитор логов Todo App")
    parser.add_argument("--monitor", "-m", action="store_true", 
                       help="Запустить мониторинг в реальном времени")
    parser.add_argument("--interval", "-i", type=int, default=30,
                       help="Интервал проверки в секундах (по умолчанию: 30)")
    parser.add_argument("--search", "-s", type=str,
                       help="Поиск в логах")
    parser.add_argument("--level", "-l", type=str, choices=["ERROR", "WARNING", "INFO", "DEBUG"],
                       help="Уровень логов для поиска")
    parser.add_argument("--hours", type=int, default=24,
                       help="Временной диапазон в часах (по умолчанию: 24)")
    parser.add_argument("--export", "-e", action="store_true",
                       help="Экспорт логов в JSON")
    
    args = parser.parse_args()
    
    monitor = LogMonitor()
    
    if args.search:
        monitor.scan_log_files()
        monitor.search_logs(args.search, args.level, args.hours)
    elif args.export:
        monitor.scan_log_files()
        monitor.export_logs(hours=args.hours)
    elif args.monitor:
        monitor.scan_log_files()
        monitor.monitor_logs(args.interval)
    else:
        # По умолчанию показываем текущее состояние
        monitor.scan_log_files()
        print("\n📊 Текущее состояние логов:")
        print("="*40)
        
        for log_file in monitor.log_files:
            file_stats = monitor.analyze_log_file(log_file)
            print(f"📄 {file_stats['filename']}: {file_stats['entries']} записей")
        
        print(f"\n💡 Используйте --help для справки по командам")


if __name__ == "__main__":
    main()
