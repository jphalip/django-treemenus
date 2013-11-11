# For Django 1.1 and under
DATABASE_ENGINE = 'django.db.backends.sqlite3'

# For Django 1.2 and above
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'treemenus',
]

ROOT_URLCONF = 'treemenus.tests.urls'

SECRET_KEY = 'Shush... Tell no one.'

# For Django 1.3 and above
STATIC_URL = '/static/'
