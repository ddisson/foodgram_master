from django.db import transaction

from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe, User
)
from users.models import Subscribe
from backend.constants import MINIMUM_AMOUNT


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient
        read_only_fields = fields


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag
        read_only_fields = fields


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=('ingredient', 'recipe')
            )
        ]


class UserRepresentationSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user, author=obj.pk).exists()


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserRepresentationSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(source='ingredient', many=True)
    tags = TagSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def _check_user_relation(self, obj, model):
        user = self.context.get('request').user
        return not user.is_anonymous and model.objects.filter(
            user=user, recipe=obj
        ).exists()

    def get_is_favorited(self, obj):
        return self._check_user_relation(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._check_user_relation(obj, ShoppingCart)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscribe.objects.filter(user=user, author=obj.author).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'is_subscribed',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserRepresentationSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeListSerializer(
            instance,
            context={'request': request}
        )
        return serializer.data

    def _create_or_update_ingredients(self, instance, ingredients_data):
        instance.ingredients.clear()
        ingredients_list = [
            IngredientRecipe(
                recipe=instance,
                ingredient=ingredient_data.get('id'),
                amount=ingredient_data.get('amount')
            )
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredients_list)

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._create_or_update_ingredients(recipe, ingredients_data)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        self._create_or_update_ingredients(instance, ingredients_data)

        return instance

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        tags_data = data.get('tags', [])

        if not tags_data:
            raise serializers.ValidationError('At least one tag is required.')

        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError(
                'Duplicate tags are not allowed.')

        if (not ingredients_data
                or not any(
                    ingredient.get('amount') > MINIMUM_AMOUNT
                    for ingredient in ingredients_data
                )):
            raise serializers.ValidationError(
                'At least one ingredient with a valid amount is required.'
            )

        ingredient_ids = [ingredient.get('id')
                          for ingredient in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Duplicate ingredients are not allowed.')

        cooking_time = data.get('cooking_time')
        if cooking_time is None or cooking_time <= 0:
            raise serializers.ValidationError(
                'A valid cooking time is required.')

        return data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')


class BriefRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
