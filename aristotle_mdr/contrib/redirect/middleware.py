from aristotle_mdr.contrib.redirect.exceptions import Redirect
from django.http import HttpResponseRedirect

class RedirectMiddleware:
    def process_exception(self, request, e):
        """Because django plugins cannot throw raw response
        """
        if isinstance(e, Redirect):
            return HttpResponseRedirect(e.url)
        return None