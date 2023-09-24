from meal import models
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

def get_user_from_token(request):
    # 1. 从请求头中提取JWT Token
    header = request.headers.get('Authorization')
    if not header:
        raise ValueError("No Authorization header provided")

    # 2. 解码Token以提取用户ID
    token = header.split(' ')[1]
    try:
        untyped_token = UntypedToken(token)
        user_id = untyped_token["user_id"]
    except (InvalidToken, TokenError, KeyError):
        raise ValueError("Invalid token")

    # 3. 使用user_id查询你的UserInfo模型
    user_info = models.UserInfo.objects.filter(id=user_id).first()
    if not user_info:
        raise ValueError("User not found")

    return user_info