
def prevent_cache_view(request):
    # Add cache headers to prevent caching of authenticated views
    request['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request['Pragma'] = 'no-cache'
    request['Expires'] = '0'
    return request
