# combined_monitor.py
import psutil
import time
import requests
import json
import os
from typing import Dict, Set

SAVE_FILE = "save.json"


# ========== Часть 1: Системный монитор ==========
def get_system_stats():
    """Получение текущих показателей системы"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        'cpu': cpu_percent,
        'memory': memory.percent,
        'disk': disk.percent
    }


def display_stats(stats):
    """Вывод статистики в консоль"""
    print("\n=== Системный монитор ===")
    print(f"Загрузка CPU:          {stats['cpu']}%")
    print(f"Использовано RAM:      {stats['memory']}%")
    print(f"Загруженность диска (/): {stats['disk']}%")
    print("=========================")


def run_system_monitor():
    """Запуск цикла системного мониторинга"""
    try:
        while True:
            stats = get_system_stats()
            display_stats(stats)
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")


# ========== Часть 2: Мониторинг курса валют ==========
class CurrencyMonitor:
    def __init__(self):
        self.rates = {}
        self.groups = {}
        self.load_groups()

    def fetch_rates(self) -> bool:
        try:
            response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=10)
            response.raise_for_status()
            data = response.json()
            self.rates = {}
            for code, info in data['Valute'].items():
                self.rates[code] = {
                    'Name': info['Name'],
                    'Value': info['Value'],
                    'Nominal': info['Nominal']
                }
            return True
        except Exception as e:
            print(f"Ошибка загрузки курсов: {e}")
            return False

    def show_all_currencies(self):
        if not self.rates:
            print("Сначала загрузите курсы (пункт 1).")
            return
        print("\n=== Все валюты ===")
        for code, info in self.rates.items():
            price = info['Value'] / info['Nominal']
            print(f"{code} - {info['Name']}: {price:.4f} RUB")
        print("=================")

    def show_currency_by_code(self, code: str):
        if not self.rates:
            print("Сначала загрузите курсы (пункт 1).")
            return
        code = code.upper()
        if code in self.rates:
            info = self.rates[code]
            price = info['Value'] / info['Nominal']
            print(f"\nКод: {code}")
            print(f"Название: {info['Name']}")
            print(f"Курс: {price:.4f} RUB")
            print(f"Номинал: {info['Nominal']} {code}")
        else:
            print(f"Валюта '{code}' не найдена.")

    def create_group(self, group_name: str):
        if group_name in self.groups:
            print(f"Группа '{group_name}' уже существует.")
            return
        self.groups[group_name] = set()
        self.save_groups()
        print(f"Группа '{group_name}' создана.")

    def add_currency_to_group(self, group_name: str, currency_code: str):
        if group_name not in self.groups:
            print(f"Группа '{group_name}' не найдена.")
            return
        currency_code = currency_code.upper()
        if not self.rates:
            print("Сначала загрузите курсы.")
            return
        if currency_code not in self.rates:
            print(f"Валюта '{currency_code}' не существует.")
            return
        self.groups[group_name].add(currency_code)
        self.save_groups()
        print(f"Валюта {currency_code} добавлена в группу '{group_name}'.")

    def remove_currency_from_group(self, group_name: str, currency_code: str):
        if group_name not in self.groups:
            print(f"Группа '{group_name}' не найдена.")
            return
        currency_code = currency_code.upper()
        if currency_code in self.groups[group_name]:
            self.groups[group_name].remove(currency_code)
            self.save_groups()
            print(f"Валюта {currency_code} удалена из группы '{group_name}'.")
        else:
            print(f"Валюта {currency_code} не найдена в группе.")

    def show_all_groups(self):
        if not self.groups:
            print("Нет созданных групп.")
            return
        if not self.rates:
            print("Сначала загрузите курсы (пункт 1).")
            return
        print("\n=== Группы валют ===")
        for group_name, currencies in self.groups.items():
            print(f"\nГруппа: {group_name}")
            if not currencies:
                print("  (нет валют)")
            else:
                for code in currencies:
                    if code in self.rates:
                        info = self.rates[code]
                        price = info['Value'] / info['Nominal']
                        print(f"  {code} - {info['Name']}: {price:.4f} RUB")
                    else:
                        print(f"  {code} - (курс недоступен)")
        print("====================")

    def save_groups(self):
        data = {name: list(currencies) for name, currencies in self.groups.items()}
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_groups(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.groups = {name: set(currencies) for name, currencies in data.items()}
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def run_currency_menu(self):
        """Меню для работы с курсами валют"""
        while True:
            print("\n" + "=" * 40)
            print("МОНИТОРИНГ КУРСА ВАЛЮТ")
            print("1. Загрузить актуальные курсы")
            print("2. Показать все валюты")
            print("3. Найти валюту по коду")
            print("4. Создать новую группу")
            print("5. Добавить валюту в группу")
            print("6. Удалить валюту из группы")
            print("7. Показать все группы")
            print("8. Вернуться в главное меню")
            print("=" * 40)
            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.fetch_rates()
            elif choice == '2':
                self.show_all_currencies()
            elif choice == '3':
                code = input("Код валюты (USD, EUR...): ").strip()
                self.show_currency_by_code(code)
            elif choice == '4':
                name = input("Название группы: ").strip()
                if name:
                    self.create_group(name)
            elif choice == '5':
                group = input("Название группы: ").strip()
                code = input("Код валюты: ").strip()
                if group and code:
                    self.add_currency_to_group(group, code)
            elif choice == '6':
                group = input("Название группы: ").strip()
                code = input("Код валюты: ").strip()
                if group and code:
                    self.remove_currency_from_group(group, code)
            elif choice == '7':
                self.show_all_groups()
            elif choice == '8':
                break
            else:
                print("Неверный ввод.")


# ========== Главное меню ==========
def main():
    print("Добро пожаловать в объединённый монитор!")
    currency_monitor = CurrencyMonitor()

    while True:
        print("\n" + "=" * 40)
        print("ГЛАВНОЕ МЕНЮ")
        print("1. Системный монитор (CPU, RAM, диск)")
        print("2. Мониторинг курса валют")
        print("3. Выход")
        print("=" * 40)
        choice = input("Выберите режим: ").strip()

        if choice == '1':
            run_system_monitor()
        elif choice == '2':
            currency_monitor.run_currency_menu()
        elif choice == '3':
            print("До свидания!")
            break
        else:
            print("Неверный ввод.")


if __name__ == "__main__":
    main()