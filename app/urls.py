# Import standard django modules
from django.conf.urls import include
from django.conf.urls import url

# Import django admin modules
from django.contrib import admin

# Import user authentication modules
from django.contrib.auth import views as auth_views

# Import rest framework modules
from rest_framework import routers

# Import app modules
from app import views


# Setup rest framework routes
router = routers.DefaultRouter()
router.register(r"state", views.StateViewSet, base_name="api-state")
router.register(r"event", views.EventViewSet, base_name="api-event")
router.register(r"recipe-transition", views.RecipeTransitionViewSet, 
                base_name="api-recipe-transition")


# Setup url patterns
urlpatterns = [
    # Admin
    url(r"^admin/", admin.site.urls),

    # Rest API
    url(r"^api/", include(router.urls, namespace='api')),

    # User management
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home/'}, name='logout'),

    # App specific
    url(r"^home/", views.Home.as_view(), name="home"),
    url(r"^recipe/", views.RecipeDashboard.as_view(), name="recipe-dashboard"),

]
 