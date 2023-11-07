from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from django.core.exceptions import ValidationError

from recipes.serializers import BriefRecipeSerializer, AuthorSerializer
from .models import User, Subscribe


class SubscribeListSerializer(AuthorSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.query_params.get('recipes_limit')
        author = get_object_or_404(User, id=obj.pk)
        recipes = author.recipes.all()
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                raise ValidationError('recipes_limit must be an integer.')
            recipes = recipes[:limit]
        serializer = BriefRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializer.data


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора'
            )
        ]

    def validate(self, data):
        user = data.get('user', self.context['request'].user)
        author = data.get('author')
        if self.context['request'].method == 'POST' and user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data
