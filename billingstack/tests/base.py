import copy
import unittest2
import mox
from oslo.config import cfg
# NOTE: Currently disabled
# from billingstack.openstack.common import policy
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.context import RequestContext, get_admin_context
from billingstack import samples
from billingstack.central import service as central_service
from billingstack import storage
from billingstack import exceptions


cfg.CONF.import_opt('storage_driver', 'billingstack.central',
                    group='service:central')
cfg.CONF.import_opt('database_connection',
                    'billingstack.storage.impl_sqlalchemy',
                    group='storage:sqlalchemy')


class AssertMixin(object):
    """
    Mixin to hold assert helpers.

    """
    def assertLen(self, expected_length, obj):
        """
        Assert a length of a object

        :param obj: The object ot run len() on
        :param expected_length: The length in Int that's expected from len(obj)
        """
        self.assertEqual(len(obj), expected_length)

    def assertData(self, expected_data, data):
        """
        A simple helper to very that at least fixture data is the same
        as returned

        :param expected_data: Data that's expected
        :param data: Data to check expected_data against
        """
        for key, value in expected_data.items():
            self.assertEqual(data[key], value)

    def assertDuplicate(self, func, *args, **kw):
        exception = kw.pop('exception', exceptions.Duplicate)
        with self.assertRaises(exception):
            func(*args, **kw)

    def assertMissing(self, func, *args, **kw):
        exception = kw.pop('exception', exceptions.NotFound)
        with self.assertRaises(exception):
            func(*args, **kw)


class TestCase(unittest2.TestCase, AssertMixin):
    def setUp(self):
        super(TestCase, self).setUp()

        self.mox = mox.Mox()

        self.config(
            rpc_backend='billingstack.openstack.common.rpc.impl_fake',
        )

        self.config(
            storage_driver='sqlalchemy',
            group='service:central'
        )

        self.config(
            database_connection='sqlite://',
            group='storage:sqlalchemy'
        )

        self.samples = samples.get_samples()

        storage.setup_schema()

        self.admin_ctxt = self.get_admin_context()

    def tearDown(self):
        # NOTE: Currently disabled
        #policy.reset()
        storage.teardown_schema()
        cfg.CONF.reset()
        self.mox.UnsetStubs()
        self.mox.VerifyAll()
        super(TestCase, self).tearDown()

    # Config Methods
    def config(self, **kwargs):
        group = kwargs.pop('group', None)

        for k, v in kwargs.iteritems():
            cfg.CONF.set_override(k, v, group)

    def get_storage_driver(self):
        connection = storage.get_connection()
        return connection

    def get_central_service(self):
        return central_service.Service()

    def get_api_service(self):
        return api_service.Service()

    def get_admin_context(self):
        return get_admin_context()

    def get_context(self, **kw):
        return RequestContext(**kw)

    def get_fixture(self, name, fixture=0, values={}):
        """
        Get a fixture from self.samples and override values if necassary
        """
        _values = copy.copy(self.samples[name][fixture])
        _values.update(values)
        return _values

    def setSamples(self):
        _, self.pg_method = self.pg_method_add()
        _, self.currency = self.currency_add()
        _, self.language = self.language_add()
        _, self.merchant = self.merchant_add()

    def language_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.language_add(ctxt, fixture, **kw)

    def currency_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.currency_add(ctxt, fixture, **kw)

    def pg_provider_register(self, fixture=0, values={}, methods=[], **kw):
        methods = [self.get_fixture('pg_method')] or methods
        fixture = self.get_fixture('pg_provider', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        data = self.central_service.pg_provider_register(ctxt, fixture, methods=methods, **kw)

        fixture['methods'] = methods
        return fixture, data

    def pg_method_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_method')
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.pg_method_add(ctxt, fixture)

    def _account_defaults(self, values):
        # NOTE: Do defaults
        if not 'currency_id' in values:
            values['currency_id'] = self.currency['id']

        if not 'language_id' in values:
            values['language_id'] = self.language['id']

    def merchant_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        self._account_defaults(fixture)

        return fixture, self.central_service.merchant_add(ctxt, fixture, **kw)

    def pg_config_add(self, provider_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_config', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.pg_config_add(ctxt, self.merchant['id'], provider_id, fixture, **kw)

    def customer_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        self._account_defaults(fixture)
        return fixture, self.central_service.customer_add(ctxt, merchant_id, fixture, **kw)

    def payment_method_add(self, customer_id, provider_method_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('payment_method', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.payment_method_add(
            ctxt, customer_id, provider_method_id, fixture, **kw)

    def user_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('user', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.user_add(ctxt, merchant_id, fixture, **kw)

    def product_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('product', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.product_add(ctxt, merchant_id, fixture, **kw)

    def plan_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('plan', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.plan_add(ctxt, merchant_id, fixture, **kw)
