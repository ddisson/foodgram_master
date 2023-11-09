from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import SubscriptionsViewSet, SubscriptionsView, UserCreateUpdateView

app_name = 'users'

router = SimpleRouter()
router.register('users', SubscriptionsViewSet, basename='user')

urlpatterns = [
    path('users/subscriptions/',
         SubscriptionsView.as_view(),
         name='subscriptions'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
     path('users/', UserCreateUpdateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserCreateUpdateView.as_view(), name='user-update'),
]
