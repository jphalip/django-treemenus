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
