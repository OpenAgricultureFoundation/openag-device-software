# Import standard django modules
from django.conf.urls import include
from django.conf.urls import url

# Import django admin modules
from django.contrib import admin

# Import user authentication modules
from django.contrib.auth import views as auth_views

# Import standard django modules
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

# Import rest framework modules
from rest_framework import routers

# Import django project settings
from django.conf import settings

# Import static files
from django.conf.urls.static import static

# Import app modules
from app import views
from app.router import Router

from connect.connect_utils import ConnectUtils


# Setup REST framework routes
router = Router()
router.register(r"state", views.StateViewSet, base_name="api-state")
router.register(r"event", views.EventViewSet, base_name="api-event")
router.register(r"recipe", views.RecipeViewSet, base_name="api-recipe")
router.register(
    r"recipe/transitions",
    views.RecipeTransitionViewSet,
    base_name="api-recipe-transition",
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
router.register(
    r"connect/status", views.ConnectGetStatus, base_name="api-connect-status"
)
router.register(r"connect/joinwifi", views.ConnectJoinWifi, base_name="api-join-wifi")
router.register(
    r"connect/deletewifis",
    views.ConnectDeleteWifis,
    base_name="api-connect-deletewifis",
)
router.register(
    r"connect/registeriot",
    views.ConnectRegisterIoT,
    base_name="api-connect-registeriot",
)
router.register(
    r"connect/deleteiotreg",
    views.ConnectDeleteIoTreg,
    base_name="api-connect-deleteiotreg",
)


# Setup dashboard redirect
def redirect_to_dashboard(request):

    # if we have a valid internet connection, go to the dashboard
    if ConnectUtils.valid_internet_connection():
        return HttpResponseRedirect(reverse("dashboard"))
    else:
        # otherwise, let the user set up their wifi connection
        return HttpResponseRedirect(reverse("connect"))


# Setup dashboard redirect
def redirect_to_login(request):
    return HttpResponseRedirect(reverse("login"))


# Setup url patterns
urlpatterns = [
    # Admin
    url(r"^admin/", admin.site.urls),
    # Rest API
    url(r"^api/", include(router.urls, namespace="api")),
    # User management
    url(
        r"^accounts/login/$",
        auth_views.login,
        {"template_name": "login.html", "redirect_authenticated_user": True},
        name="login",
    ),
    url(r"^logout/$", auth_views.logout, {"next_page": "/"}, name="logout"),
    url(r"^password/$", views.change_password, name="change_password"),
    # App specific
    url(r"^$", redirect_to_dashboard, name="home"),
    url(r"^dashboard/$", views.Dashboard.as_view(), name="dashboard"),
    url(r"^config/$", views.DeviceConfig.as_view(), name="device-config"),
    url(r"^peripherals/$", views.Peripherals.as_view(), name="peripherals"),
    url(r"^logs/$", views.Logs.as_view(), name="logs"),
    url(r"^events/$", views.Events.as_view(), name="events"),
    url(r"^recipes/$", views.Recipes.as_view(), name="recipes"),
    url(r"^recipe/build/$", views.RecipeBuilder.as_view(), name="recipe-builder"),
    url(r"^environments/$", views.Environments.as_view(), name="environments"),
    url(r"^iot/$", views.IoT.as_view(), name="iot"),
    url(r"^resource/$", views.Resource.as_view(), name="resource"),
    url(r"^connect/$", views.Connect.as_view(), name="connect"),
    url(r"^upgrade/$", views.Upgrade.as_view(), name="upgrade"),
    url(r"^manual/$", views.Manual.as_view(), name="manual"),
    url(r"^entry/$", views.Entry.as_view(), name="entry"),
    url(r"^scratchpad/$", views.Scratchpad.as_view(), name="entry"),
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
