import os
from urllib.parse import unquote

from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from django.core.files.storage import default_storage

from .models import Template


def media_template_fallback(request, subpath: str):
    """Serve or redirect media template requests to a normalized filename when possible.

    - `subpath` is the path under MEDIA_ROOT (e.g. 'templates/Some_File_RibwlEF.pdf')
    - If the requested file exists in storage, redirect to its storage URL.
    - Otherwise try to compute a normalized filename (using Template._normalize_filename)
      and redirect to that if it exists.
    - If no candidate exists, return 404 so normal static handler can respond.
    """
    # Only handle templates folder
    if not subpath.startswith('templates/'):
        return HttpResponseNotFound()

    # Normalize percent-encoding and path separators
    requested = unquote(subpath)

    # If file exists as requested, redirect to its URL
    if default_storage.exists(requested):
        return redirect(default_storage.url(requested))

    # Try to compute candidate name by stripping the token (keeping accents)
    directory, basename = os.path.split(requested)
    base, ext = os.path.splitext(basename)
    # Strip trailing underscore+token before extension
    import re
    base = re.sub(r'_[A-Za-z0-9]+$', '', base)
    candidate = os.path.join(directory, f"{base}{ext}")

    if candidate != requested and default_storage.exists(candidate):
        return redirect(default_storage.url(candidate))

    return HttpResponseNotFound()
