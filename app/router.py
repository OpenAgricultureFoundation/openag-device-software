# Import standard python modules
import re
from collections import OrderedDict

# Import python types
from typing import Dict, Any, List

# Import django modules
from django.urls import NoReverseMatch

# Import django rest modules
from rest_framework import routers, views
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.request import Request

# Import device utilities
from device.utilities import logger


class Router(routers.DefaultRouter):
    """Custom router."""

    # Initialize logger
    logger = logger.Logger("Router", "app")

    def get_api_root_view(self, api_urls: List[str] = None) -> Dict:
        """Gets api root view."""
        self.logger.debug("Getting api root view")
        api_root_dict: Dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRootView(views.APIView):
            """ The default basic root view for DefaultRouter """

            _ignore_model_permissions = True
            schema = None  # exclude from schema
            api_root_dict: Dict = {}

            def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
                # Return a plain {"name": "hyperlink"} response.
                response: Dict = OrderedDict()
                namespace = request.resolver_match.namespace
                for key, url_name in self.api_root_dict.items():
                    if namespace:
                        url_name = namespace + ":" + url_name
                    try:
                        response[key] = reverse(
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
                base = response["state"].split("api", 1)[0] + "api/"
                for endpoint in endpoints:
                    response[endpoint] = base + endpoint

                return Response(response, 200)

        return APIRootView.as_view(api_root_dict=api_root_dict)
