# Import django modules
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

# Import rest framework modules
from rest_framework import routers

# Import app modules
from app import views
from app.router import Router

# Setup django rest routes
router = Router()
router.register(r"state", views.StateViewSet, base_name="api-state")
router.register(r"event", views.EventViewSet, base_name="api-event")
router.register(r"recipe", views.RecipeViewSet, base_name="api-recipe")
router.register(
    r"recipe/transitions",
    views.RecipeTransitionViewSet,
    base_name="api-recipe-transition",
)
router.register(
    r"config/device", views.DeviceConfigViewSet, base_name="api-config-device"
)
router.register(r"cultivars", views.CultivarViewSet, base_name="api-cultivars")
router.register(
    r"cultivation-methods",
    views.CultivationMethodViewSet,
    base_name="api-cultivation-methods",
)
router.register(
    r"peripheral/setups",
    views.PeripheralSetupViewSet,
    base_name="api-peripheral-setups",
)
router.register(
    r"variables/sensor", views.SensorVariableViewSet, base_name="api-sensor-variables"
)
router.register(
    r"variables/actuator",
    views.ActuatorVariableViewSet,
    base_name="api-actuator-variables",
)
router.register(r"system", views.SystemViewSet, base_name="api-system")
router.register(r"network", views.NetworkViewSet, base_name="api-network")
router.register(r"upgrade", views.UpgradeViewSet, base_name="api-upgrade")
router.register(r"iot", views.IotViewSet, base_name="api-iot")
router.register(r"led", views.LEDViewSet, base_name="api-led")

# Initialize url pattern parameters
login_settings = {"template_name": "login.html", "redirect_authenticated_user": True}
connect_advanced_view = views.ConnectAdvanced.as_view()

# Setup url patterns
urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api/", include(router.urls, namespace="api")),
    url(r"^accounts/login/$", auth_views.login, login_settings, name="login"),
    url(r"^accounts/logout/$", auth_views.logout, {"next_page": "/"}, name="logout"),
    url(r"^password/$", views.change_password, name="change_password"),
    url(r"^dashboard/$", views.Dashboard.as_view(), name="dashboard"),
    url(r"^config/$", views.DeviceConfig.as_view(), name="device-config"),
    url(r"^peripherals/$", views.Peripherals.as_view(), name="peripherals"),
    url(r"^images/$", views.Images.as_view(), name="images"),
    url(r"^logs/$", views.Logs.as_view(), name="logs"),
    url(r"^recipes/$", views.Recipes.as_view(), name="recipes"),
    url(r"^environments/$", views.Environments.as_view(), name="environments"),
    url(r"^iot/$", views.IoT.as_view(), name="iot"),
    url(r"^resource/$", views.Resource.as_view(), name="resource"),
    url(r"^$", views.Connect.as_view(), name="connect"),
    url(r"^upgrade/$", views.Upgrade.as_view(), name="upgrade"),
    url(r"^connect_advanced/$", connect_advanced_view, name="connect_advanced"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
