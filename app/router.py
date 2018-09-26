import re
from rest_framework import routers
from rest_framework import views
from collections import OrderedDict
from django.urls import NoReverseMatch
from rest_framework.reverse import reverse
from rest_framework.response import Response


class Router(routers.DefaultRouter):
    def get_api_root_view(self, api_urls=None):
        """
        Return a basic root view.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRootView(views.APIView):
            """ The default basic root view for DefaultRouter """

            _ignore_model_permissions = True
            schema = None  # exclude from schema
            api_root_dict = None

            def get(self, request, *args, **kwargs):
                # Return a plain {"name": "hyperlink"} response.
                ret = OrderedDict()
                namespace = request.resolver_match.namespace
                for key, url_name in self.api_root_dict.items():
                    if namespace:
                        url_name = namespace + ":" + url_name
                    try:
                        ret[key] = reverse(
                            url_name,
                            args=args,
                            kwargs=kwargs,
                            request=request,
                            format=kwargs.get("format", None),
                        )
                    except NoReverseMatch:
                        # Don't bail out if eg. no list routes exist, only detail routes.
                        continue

                # Add APIView endpoints
                endpoints = ["recipe/stop", "recipe/{uuid}/start/"]
                base = ret["state"].split("api", 1)[0] + "api/"
                for endpoint in endpoints:
                    ret[endpoint] = base + endpoint

                return Response(ret)

        return APIRootView.as_view(api_root_dict=api_root_dict)
