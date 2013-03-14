from billingstack.openstack.common.context import get_admin_context
from billingstack.payment_gateway import register_providers
from billingstack.manage.base import ListCommand
from billingstack.manage.database import DatabaseCommand


class ProvidersRegister(DatabaseCommand):
    """
    Register Payment Gateway Providers
    """
    def execute(self, parsed_args):
        context = get_admin_context()
        register_providers(context)


class ProvidersList(DatabaseCommand, ListCommand):
    def execute(self, parsed_args):
        context = get_admin_context()
        data = self.conn.list_pg_provider(context)

        for p in data:
            keys = ['type', 'name']
            methods = [":".join([m[k] for k in keys]) for m in p['methods']]
            p['methods'] = ", ".join(methods)
        return data
