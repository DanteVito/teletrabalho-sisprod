from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class RPRAccount(ProviderAccount):
    pass


class RPRProvider(OAuthProvider):

    id = 'provider'
    name = 'ReceitaPR'
    account_class = RPRAccount

    def extract_uid(self, data):
        return str(data['chaveusuario'])

    def extract_common_fields(self, data):
        return dict(
                    email=data['email'],
                    name=data['nmusuario'],)

    # def get_default_scope(self):
    #     pass


providers.registry.register(RPRProvider)