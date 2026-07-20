from rest_framework.routers import SimpleRouter

from .views import EmployeeViewSet

app_name = "employees"

router = SimpleRouter()
router.register("", EmployeeViewSet, basename="employee")

urlpatterns = router.urls
