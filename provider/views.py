import json
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter, OAuthLoginView, OAuthCallbackView)
from .provider import RPRProvider
from django.conf import settings

class RPRApi(OAuth):
    url = f'{settings.OAUTH_SERVER_BASEURL}/portal/v1.0/usuarios/autenticacao'

    def get_user_info(self):
        user = json.loads(self.query(self.url))
        return user

class RPRAdapter(OAuthAdapter):
    provider_id = RPRProvider.id

    request_token_url = f'{settings.OAUTH_SERVER_BASEURL}/oauth/v1.0/request_token'
    access_token_url = f'{settings.OAUTH_SERVER_BASEURL}/oauth/v1.0/access_token'
    authorize_url = f'{settings.OAUTH_SERVER_BASEURL}/oauth/v1.0/authorize'

    def complete_login(self, request, app, token, response):
        client = RPRApi(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)

oauth_login = OAuthLoginView.adapter_view(RPRAdapter)
oauth_callback = OAuthCallbackView.adapter_view(RPRAdapter)