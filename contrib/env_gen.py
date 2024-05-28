"""
Python SECRET_KEY generator.

Instructions: Run this script in the source dir of the project.
It will be created a file .env with environment variables for python-decouple

use:
> python contrib/env_gen.py

"""

import random

CHARS = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?@#$%^&*()"
SIZE = 50
SECRET_KEY = "".join(random.sample(CHARS, SIZE))

CHARS = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?@#$%_"
SIZE = 20
PASSWORD = "".join(random.sample(CHARS, SIZE))

CHARS = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?@#$%_"
SIZE = 8
PASSWORD_ADMIN = "".join(random.sample(CHARS, SIZE))

CONFIG_STRING = """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost
#DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
#POSTGRES_DB=
#POSTGRES_USER=
#POSTGRES_PASSWORD=%s
#DB_HOST=localhost
#DEFAULT_FROM_EMAIL=
#EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#EMAIL_HOST=localhost
#EMAIL_PORT=
#EMAIL_HOST_USER=
#EMAIL_HOST_PASSWORD=
#EMAIL_USE_TLS=True
PASSWORD_ADMIN=%s
""".strip() % (
    SECRET_KEY,
    PASSWORD,
    PASSWORD_ADMIN,
)

# Writing our configuration file to '.env'
with open(".env", "w", encoding="utf-8") as configfile:
    configfile.write(CONFIG_STRING)

print("Success!")
print("Type: cat .env")
