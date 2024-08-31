from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from .provider import RPRProvider

urlpatterns = default_urlpatterns(RPRProvider)