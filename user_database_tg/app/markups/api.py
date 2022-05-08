from user_database_tg.app.markups.utils import get_inline_keyboard


def get_api_menu():
    keyboard = [
        (("API Профиль", "api_profile"),),
        (("Купить подписку API", "buy_api"),),
        (("Получить токен", "get_token"),),
    ]
    return get_inline_keyboard(keyboard)
