from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import serializers


from users.models import Subscribe
from .models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe, User
)

from backend.constants import INVALID_COOKING_TIME_NUMBER


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


class AuthorSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return not user.is_anonymous and user.following.filter(author=obj).exists()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all())
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')



class RecipeListSerializer(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(source='ingredient', many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def _check_user_relation(self, obj, model):
        user = self.context.get('request').user
        return not user.is_anonymous and model.objects.filter(user=user, recipe=obj).exists()


    def get_is_favorited(self, obj):
        return self._check_user_relation(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._check_user_relation(obj, ShoppingCart)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeListSerializer(
            instance,
            context={'request': request}
        ).data

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

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError({
                'ingredients': 'At least one ingredient is required.'
            })

        tags_data = data.get('tags', [])
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError({
                'tags': 'Duplicate tags are not allowed.'
            })


        cooking_time = data.get('cooking_time')
        if cooking_time is None or cooking_time <= INVALID_COOKING_TIME_NUMBER:
            raise serializers.ValidationError({
                'cooking_time': 'A valid cooking time is required.'
            })

        ingredient_ids = [ingredient['id'] for ingredient in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Duplicate ingredients are not allowed.'
            })

        return data

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

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class BriefRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
