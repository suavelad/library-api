from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users import views as view

router = DefaultRouter()
router.register("", view.AuthViewSet, "auth")

urlpatterns = router.urls
