from rest_framework.routers import SimpleRouter

from .views import PositionViewSet

app_name = "positions"

router = SimpleRouter()
router.register("", PositionViewSet, basename="position")

urlpatterns = router.urls
