from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import User, Subscribe
from .serializers import (
    SubscribeListSerializer,
    SubscribeCreateSerializer,
    UserModificationSerializer, UserWithRecipesSerializer
)


class UserCreateUpdateView(APIView):
    def post(self, request):
        serializer = UserModificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserModificationSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscribeListSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscriptionsViewSet(viewsets.ModelViewSet):

    @action(detail=True, permission_classes=[permissions.IsAuthenticated], methods=['post'])
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('pk'))

        if user == author:
            return Response({'errors': 'You cannot subscribe to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if Subscribe.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'You are already subscribed to this author.'}, status=status.HTTP_400_BAD_REQUEST)

        subscribe = Subscribe.objects.create(user=user, author=author)
        subscribe_serializer = UserWithRecipesSerializer(author, context={'request': request})
        return Response(subscribe_serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        id = kwargs.get('pk')
        user = self.request.user
        author = get_object_or_404(User, id=id)
        follow = Subscribe.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(
                {'detail': 'Вы отписались от автора'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'detail': 'Вы не были подписаны на данного автора'},
            status=status.HTTP_400_BAD_REQUEST
        )