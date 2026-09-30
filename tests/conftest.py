import sys
from pathlib import Path

# the test-suite relies on the example project's ``blog`` app
EXAMPLE_PROJECT = Path(__file__).resolve().parent.parent / 'example_project'
sys.path.insert(0, str(EXAMPLE_PROJECT))


def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SITE_ID=1,
        SECRET_KEY='HitCounts Rock!',
        DEBUG=True,
        ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
        USE_I18N=True,
        USE_TZ=True,
        STATIC_URL='/static/',
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
        MIDDLEWARE=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            'blog',
            'hitcount',
            'tests',
        ),
        ROOT_URLCONF='example_project.urls',
        SESSION_ENGINE='django.contrib.sessions.backends.db',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        # HitCount Variables (default values)
        HITCOUNT_KEEP_HIT_ACTIVE={'days': 7},
        HITCOUNT_HITS_PER_IP_LIMIT=0,
        HITCOUNT_EXCLUDE_USER_GROUP=(),
        HITCOUNT_KEEP_HIT_IN_DATABASE={'days': 30},
    )

    import django
    django.setup()

    return settings
