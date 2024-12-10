from django.http import HttpResponseRedirect

class RestrictAllauthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_paths = [
        '/accounts/login/',
        '/accounts/logout/',
        '/accounts/password/change/',
        '/accounts/password/reset/',
        '/accounts/signup/',
        '/accounts/social/signup/',
        '/accounts/social/connections/',
]
        if request.path in restricted_paths:
            return HttpResponseRedirect('/')
        return self.get_response(request)
