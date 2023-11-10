import os

# Tag constants
TAG_NAME_MAX_LENGTH = 20
TAG_SLUG_MAX_LENGTH = 20
TAG_COLOR_MAX_LENGTH = 7
TAG_COLOR_DEFAULT = '#49B64E'

# Recipe constants
RECIPE_MAX_LENGTH = 200

# Ingredient constants
INGREDIENTS_NAME_MAX_LENGTH = 200
INGREDIENTS_MEASUREMENT_MAX_LENGTH = 20

# SERIALIZERS
MINIMUM_AMOUNT = 0

# User constants
USER_NAME_MAX_LENGTH = 150
USER_MAIL_MAX_LENGTH = 254

# pdf shoppinglist
FONTS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 'services',
                 'fonts')
)
HEADER_FONT_SIZE = 28
HEADER_TOP_MARGIN = 20
HEADER_BOTTOM_MARGIN = 35
BODY_FONT_SIZE = 14
BODY_LINE_SPACING = 12
TEXT_TOP_MARGIN = 10
TEXT_BOTTOM_MARGIN = 12
TEXT_RIGHT_MARGIN = 12
TEXT_LEFT_MARGIN = 50
SPACER = 1
STREAM_POSITION = 0

# Verbose names
EMAIL_VERBOSE_NAME = 'адрес электронной почты'
USERNAME_VERBOSE_NAME = 'логин'
FOLLOWER_VERBOSE_NAME = 'Подписчик'
AUTHOR_VERBOSE_NAME = 'Автор'
USER_VERBOSE_NAME = 'Пользователь'
SUBSCRIBE_VERBOSE_NAME = 'Подписка'

# Error messages
EMAIL_ALREADY_REGISTERED = 'Такой адрес электронной почты уже зарегистрирован.'
USERNAME_ALREADY_REGISTERED = (
    'Пользователь с таким именем уже '
    'зарегистрирован.'
)
USERNAME_CANNOT_BE_ME = 'Username не может быть "me".'
USERS_CANNOT_SUBSCRIBE_TO_THEMSELVES = (
    "Пользователи не могут подписаться на себя."
)

# Other constants
USERNAME_HELP_TEXT = 'Не более 150 символов.'
USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
USERS_GET_SHORT_NAME = 15

# Validators
HEX_COLOR_PATTERN = r'^#[a-fA-F0-9]{6}$'
HEX_COLOR_MESSAGE = 'Enter a valid HEX color. (e.g., "#FF0033")'
HEX_COLOR_DEFAULT = '#49B64E'
MIN_COOKING_TIME = 1
COOKING_TIME_ERROR_MESSAGE = 'Время приготовления должно быть больше 1 минуты'
MIN_AMOUNT = 1
AMOUNT_ERROR_MESSAGE = 'Количество не может быть меньше 1'
