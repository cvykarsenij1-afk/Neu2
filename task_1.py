import requests
from requests.exceptions import RequestException

urls = [
    "https://github.com/",
    "https://www.binance.com/en",
    "https://tomtit.tomsk.ru/",
    "https://jsonplaceholder.typicode.com/",
    "https://moodle.tomtit-tomsk.ru/"
]

def get_status_text(code: int) -> str:
    if code == 200:
        return "доступен"
    elif code == 403:
        return "вход запрещен"
    elif code == 404:
        return "не найден"
    else:
        return "не доступен"

def check_url(url: str, timeout: int = 10) -> tuple:
