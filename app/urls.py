# Import standard django modules
from django.conf.urls import include
from django.conf.urls import url

# Import django admin modules
from django.contrib import admin

# Import user authentication modules
from django.contrib.auth import views as auth_views

# Import standard django
from django.urls import reverse
from django.http import HttpResponseRedirect

# Import rest framework modules
from rest_framework import routers

# Import django project settings
from django.conf import settings

# Import static files
from django.conf.urls.static import static

# Import app modules
from app import views
from app.router import Router


# Setup rest framework routes
router = Router()
router.register(r"state", views.StateViewSet, base_name="api-state")
router.register(r"event", views.EventViewSet, base_name="api-event")
router.register(r"recipe", views.RecipeViewSet, base_name="api-recipe")
router.register(r"recipe/transitions", views.RecipeTransitionViewSet, base_name="api-recipe-transition")
router.register(r"cultivars", views.CultivarViewSet, base_name="api-cultivars")
router.register(r"cultivation-methods", views.CultivationMethodViewSet, base_name="api-cultivation-methods")
router.register(r"peripheral/setups", views.PeripheralSetupViewSet, base_name="api-peripheral-setups")

# Setup dashboard redirect
def redirect_to_dashboard(request):
    return HttpResponseRedirect(reverse('dashboard'))

# Setup url patterns
urlpatterns = [
    # Admin
    url(r"^admin/", admin.site.urls),

    # Rest API
    url(r"^api/", include(router.urls, namespace="api")),

    # User management
    url(r"^login/$", auth_views.login, {"template_name": "login.html"}, name="login"),
    url(r"^logout/$", auth_views.logout, {"next_page": "/"}, name="logout"),

    # App specific
    url(r'^$', redirect_to_dashboard, name="home"),
    url(r'^dashboard/$', views.Dashboard.as_view(), name="dashboard"),
    url(r'^peripherals/$', views.Peripherals.as_view(), name="peripherals"),
    url(r'^events/$', views.Events.as_view(), name="events"),
    url(r'^recipes/$', views.Recipes.as_view(), name="recipes"),
    url(r'^recipe/build/$', views.RecipeBuilder.as_view(), name="recipe-builder"),
    url(r'^environments/$', views.Environments.as_view(), name="environments"),
    url(r'^manual/$', views.Manual.as_view(), name="manual"),
    url(r'^entry/$', views.Entry.as_view(), name="entry"),
    url(r'^scratchpad/$', views.Scratchpad.as_view(), name="entry"),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

