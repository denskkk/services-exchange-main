from django.http import HttpRequest


def user_mode(request: HttpRequest) -> dict:
    """
    Помещает в контекст режим пользователя `user_mode` - buyer или seller.
    Доступен во всех шаблонах как {{ user_mode }}.
    """
    mode = request.session.get("user_mode")

    if mode not in ["buyer", "seller"]:
        mode = "seller"

    return {
        "user_mode": mode,
    }
