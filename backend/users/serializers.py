from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from recipes.serializers import (
    BriefRecipeSerializer,
    UserRepresentationSerializer
)
from .models import User, Subscribe


class UserModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

    def validate_password(self, value):
        validate_password(value)
        return value


class SubscribeListSerializer(UserRepresentationSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(UserRepresentationSerializer.Meta):
        fields = UserRepresentationSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        queryset = obj.recipes.all()
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    'recipes_limit must be an integer')
        return BriefRecipeSerializer(
            queryset,
            many=True,
            context={'request': request}
        ).data


class UserWithRecipesSerializer(serializers.ModelSerializer):
    recipes = BriefRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        if self.context['request'].method == 'POST' and user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data
