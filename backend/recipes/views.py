from django.db.models import Sum
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Ingredient, Tag, Recipe,
    Favorite, ShoppingCart, IngredientRecipe
)
from .permissions import IsAuthenticatedOwnerOrReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    BriefRecipeSerializer
)
from backend.services.shoplist import download_pdf


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _handle_favorite_shopping(self, request, pk, model, errors):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj, created = model.objects.get_or_create(user=request.user, recipe=recipe)

        if request.method == 'POST':
            if not created:
                return Response(errors['recipe_in'], status=status.HTTP_400_BAD_REQUEST)

            serializer = BriefRecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if created:
                return Response(errors['recipe_not_in'], status=status.HTTP_400_BAD_REQUEST)

            obj.delete()
            return Response({'msg': 'Успешно удалено'}, status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        errors = {
            'recipe_in': {'errors': 'Рецепт уже в избранном'},
            'recipe_not_in': {'error': 'Рецепта нет в избранном'}
        }
        return self._handle_favorite_shopping(
            request,
            pk,
            Favorite,
            errors
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        errors = {
            'recipe_in': {'errors': 'Рецепт уже в списке покупок'},
            'recipe_not_in': {'error': 'Рецепта нет в списке покупок'}
        }
        return self._handle_favorite_shopping(
            request,
            pk,
            ShoppingCart,
            errors
        )

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny])
    def download_shopping_cart(self, request):
        ingredients_obj = (
            IngredientRecipe.objects.filter(recipe__carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(sum_amount=Sum('amount'))
        )
        data_dict = {}
        ingredients_list = []
        for item in ingredients_obj:
            name = item['ingredient__name'].capitalize()
            unit = item['ingredient__measurement_unit']
            sum_amount = item['sum_amount']
            data_dict[name] = [sum_amount, unit]
        for ind, (key, value) in enumerate(data_dict.items(), 1):
            if ind < 10:
                ind = '0' + str(ind)
            ingredients_list.append(
                f'{ind}. {key} - ' f'{value[0]} ' f'{value[1]}'
            )
        return download_pdf(ingredients_list)
