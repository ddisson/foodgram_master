from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models

from backend.constants import (
    TAG_NAME_MAX_LENGTH, TAG_SLUG_MAX_LENGTH,
    RECIPE_MAX_LENGTH, INGREDIENTS_NAME_MAX_LENGTH,
    INGREDIENTS_MEASUREMENT_MAX_LENGTH,
    HEX_COLOR_PATTERN, HEX_COLOR_MESSAGE, HEX_COLOR_DEFAULT,
    MIN_COOKING_TIME, COOKING_TIME_ERROR_MESSAGE,
    MIN_AMOUNT, AMOUNT_ERROR_MESSAGE
)

User = get_user_model()

color_validator = RegexValidator(
    HEX_COLOR_PATTERN,
    HEX_COLOR_MESSAGE
)


class Tag(models.Model):
    name = models.CharField('Название тэга', unique=True,
                            max_length=TAG_NAME_MAX_LENGTH)
    slug = models.SlugField('Адрес тэга', unique=True,
                            max_length=TAG_SLUG_MAX_LENGTH)
    color = models.CharField(
        'Цвет(HEX)',
        unique=True, max_length=7,
        default=HEX_COLOR_DEFAULT,
        validators=[color_validator]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента',
                            max_length=INGREDIENTS_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Еденицы измерения', max_length=INGREDIENTS_MEASUREMENT_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField('Название рецепта', max_length=RECIPE_MAX_LENGTH)
    text = models.TextField('Описание')
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME, message=COOKING_TIME_ERROR_MESSAGE)
        ],
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', related_name='recipes')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} ({self.author})'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=[MinValueValidator(
            MIN_AMOUNT, message=AMOUNT_ERROR_MESSAGE)]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique ingredient recipe'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='uniq_favorite_user_recipe')
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uniq_cart_user_recipe'
            )
        ]
