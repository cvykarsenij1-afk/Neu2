import psutil
import time
import sys


def get_system_stats():
    """Получение текущих показателей системы"""
    cpu_percent = psutil.cpu_percent(interval=1)  # загрузка CPU за 1 секунду
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        'cpu': cpu_percent,
        'memory_used': memory.used,
        'memory_total': memory.total,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent
    }


def format_bytes(bytes_val):
    """Преобразование байтов в читаемый формат (ГБ/МБ)"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} ТБ"


def main():
    print("=== Системный монитор ===")
    print("Для выхода нажмите Ctrl+C\n")

    try:
        while True:
            stats = get_system_stats()

            # Очистка экрана (для разных ОС)
            print("\033c", end="")  # для Linux/macOS
            # print(chr(27) + "[2J" + chr(27) + "[;H", end="")  # альтернативный вариант

            print(f"Загрузка CPU:         {stats['cpu']:.1f}%")
            print(
                f"Оперативная память:   {format_bytes(stats['memory_used'])} / {format_bytes(stats['memory_total'])}  ({stats['memory_percent']:.1f}%)")
            print(f"Загруженность диска (C:/): {stats['disk_percent']:.1f}%")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nЗавершение работы...")
        sys.exit(0)


if __name__ == "__main__":
    main()