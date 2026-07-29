from rest_framework.routers import SimpleRouter

from .views import DepartmentViewSet

app_name = "departments"

router = SimpleRouter()
router.register("", DepartmentViewSet, basename="department")

urlpatterns = router.urls
