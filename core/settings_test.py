from .settings import *

# Override settings for testing
# Keep the api app for testing
# INSTALLED_APPS remains the same

# Remove problematic imports for testing
MIDDLEWARE = [
    mw for mw in MIDDLEWARE if mw != 'api.middleware.AuditLogMiddleware'
]

# Use in-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable file storage for tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Test settings
SECRET_KEY = 'test-secret-key'
DEBUG = True
USE_TZ = True
