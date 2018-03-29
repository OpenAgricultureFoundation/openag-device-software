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
router.register(r"users", views.UserViewSet, base_name="api-users")
router.register(r"groups", views.GroupViewSet, base_name="api-groups")
router.register(r"event", views.EventViewSet, base_name="api-event")


# Setup url patterns
urlpatterns = [
    # Admin
    url(r"^admin/", admin.site.urls),

    # Rest API
    url(r"^api/", include(router.urls, namespace='api')),

    # User authentication
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    
    # App specific
    url(r"^", views.home),
    url(r"^event/", views.EventList.as_view()),
]
 