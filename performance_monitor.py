#!/usr/bin/env python3
"""
Скрипт для мониторинга производительности Todo App
"""
import time
import requests
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any

class PerformanceMonitor:
    """Монитор производительности API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def measure_endpoint(self, endpoint: str, method: str = "GET", 
                        data: Dict[str, Any] = None, headers: Dict[str, str] = None,
                        iterations: int = 10) -> Dict[str, Any]:
        """Измерение производительности эндпоинта"""
        print(f"📊 Тестирование {method} {endpoint} ({iterations} итераций)...")
        
        response_times = []
        status_codes = []
        errors = []
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                if method.upper() == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                elif method.upper() == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", 
                                          json=data, headers=headers)
                elif method.upper() == "PUT":
                    response = requests.put(f"{self.base_url}{endpoint}", 
                                          json=data, headers=headers)
                elif method.upper() == "DELETE":
                    response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)
                else:
                    raise ValueError(f"Неподдерживаемый метод: {method}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # в миллисекундах
                
                response_times.append(response_time)
                status_codes.append(response.status_code)
                
                if response.status_code >= 400:
                    errors.append({
                        "iteration": i + 1,
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    })
                
                # Небольшая пауза между запросами
                time.sleep(0.1)
                
            except Exception as e:
                errors.append({
                    "iteration": i + 1,
                    "error": str(e)
                })
        
        # Статистика
        if response_times:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "min_time": min(response_times),
                "max_time": max(response_times),
                "avg_time": statistics.mean(response_times),
                "median_time": statistics.median(response_times),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "success_rate": (len(response_times) - len(errors)) / len(response_times) * 100,
                "errors": errors,
                "status_codes": status_codes
            }
        else:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": 0
            }
        
        self.results.append(stats)
        return stats
    
    def print_results(self):
        """Вывод результатов тестирования"""
        print("\n" + "="*80)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*80)
        
        for result in self.results:
            print(f"\n🔗 {result['method']} {result['endpoint']}")
            print(f"   Итераций: {result['iterations']}")
            
            if 'avg_time' in result:
                print(f"   Время ответа:")
                print(f"     Минимум: {result['min_time']:.2f} мс")
                print(f"     Максимум: {result['max_time']:.2f} мс")
                print(f"     Среднее: {result['avg_time']:.2f} мс")
                print(f"     Медиана: {result['median_time']:.2f} мс")
                print(f"     Стандартное отклонение: {result['std_dev']:.2f} мс")
            
            print(f"   Успешность: {result['success_rate']:.1f}%")
            
            if result['errors']:
                print(f"   Ошибки: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Показываем только первые 3 ошибки
                    if 'status_code' in error:
                        print(f"     Итерация {error['iteration']}: HTTP {error['status_code']}")
                    else:
                        print(f"     Итерация {error['iteration']}: {error['error']}")
    
    def save_results(self, filename: str = None):
        """Сохранение результатов в файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Результаты сохранены в {filename}")
    
    def run_basic_tests(self):
        """Запуск базовых тестов производительности"""
        print("🚀 Запуск базовых тестов производительности")
        print("="*50)
        
        # Тест корневого эндпоинта
        self.measure_endpoint("/", "GET")
        
        # Тест health check
        self.measure_endpoint("/health", "GET")
        
        # Тест информации о приложении
        self.measure_endpoint("/info", "GET")
        
        # Тест документации
        self.measure_endpoint("/docs", "GET")
        
        # Тест OpenAPI схемы
        self.measure_endpoint("/openapi.json", "GET")
        
        # Тест защищенных эндпоинтов (должны вернуть 401)
        self.measure_endpoint("/api/v1/users/", "GET")
        self.measure_endpoint("/api/v1/todos/", "GET")
        self.measure_endpoint("/api/v1/categories/", "GET")
    
    def run_api_tests(self, auth_token: str = None):
        """Запуск тестов API с аутентификацией"""
        if not auth_token:
            print("⚠️  Токен аутентификации не предоставлен, пропускаем API тесты")
            return
        
        print("\n🔐 Запуск тестов API с аутентификацией")
        print("="*50)
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Тест профиля пользователя
        self.measure_endpoint("/api/v1/users/me", "GET", headers=headers)
        
        # Тест списка пользователей
        self.measure_endpoint("/api/v1/users/", "GET", headers=headers)
        
        # Тест списка задач
        self.measure_endpoint("/api/v1/todos/", "GET", headers=headers)
        
        # Тест списка категорий
        self.measure_endpoint("/api/v1/categories/", "GET", headers=headers)


def main():
    """Основная функция"""
    print("🚀 Мониторинг производительности Todo App")
    print("="*50)
    
    # Создаем монитор
    monitor = PerformanceMonitor()
    
    # Запускаем базовые тесты
    monitor.run_basic_tests()
    
    # Выводим результаты
    monitor.print_results()
    
    # Сохраняем результаты
    monitor.save_results()
    
    print("\n🎉 Тестирование завершено!")


if __name__ == "__main__":
    main()
