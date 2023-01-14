import locale

_ = {
    'ru_RU': {
        'Regular expression': 'Регулярное выражение',
        'Close': 'Закрыть',
        'Case-sensitive search': 'Регистрозависимый поиск',
        'Dark mode': 'Темная тема',
    },
}


def gettext(text: str) -> str:
    lang = locale.getdefaultlocale()[0]
    if lang in _:
        if text in _[lang]:
            return _[lang][text]
    return text
