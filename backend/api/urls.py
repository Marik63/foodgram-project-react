from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UsersViewSet
)


router = DefaultRouter()

router.register(r'users', UsersViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
