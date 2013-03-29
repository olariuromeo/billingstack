# -*- encoding: utf-8 -*-
#
# Author: Endre Karlson <endre.karlson@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from wsme.types import text, DictType


from billingstack.api.base import ModelBase, property_type
from billingstack.openstack.common import log

LOG = log.getLogger(__name__)


class Base(ModelBase):
    id = text


class DescribedBase(Base):
    name = text
    title = text
    description = text


def change_suffixes(data, keys, shorten=True, suffix='_name'):
    """
    Loop thro the keys foreach key setting for example
    'currency_name' > 'currency'
    """
    for key in keys:
        if shorten:
            new, old = key, key + suffix
        else:
            new, old = key + suffix, key
        if old in data:
            if new in data:
                raise RuntimeError("Can't override old key with new key")

            data[new] = data.pop(old)


class Currency(DescribedBase):
    pass


class Language(DescribedBase):
    pass


class InvoiceState(DescribedBase):
    pass


class PGMethod(DescribedBase):
    type = text


class PGProvider(DescribedBase):
    def __init__(self, **kw):
        kw['methods'] = [PGMethod.from_db(m) for m in kw.get('methods', {})]
        super(PGProvider, self).__init__(**kw)

    methods = [PGMethod]
    properties = DictType(key_type=text, value_type=property_type)


class ContactInfo(Base):
    id = text
    first_name = text
    last_name = text
    company = text
    address1 = text
    address2 = text
    address3 = text
    locality = text
    region = text
    country_name = text
    postal_code = text

    phone = text
    email = text
    website = text


class PlanItem(Base):
    plan_id = text
    product_id = text

    pricing = DictType(key_type=text, value_type=property_type)


class Plan(DescribedBase):
    def __init__(self, **kw):
        kw['items'] = map(PlanItem.from_db, kw.pop('items', []))
        super(Plan, self).__init__(**kw)

    items = [PlanItem]
    properties = DictType(key_type=text, value_type=property_type)


class Product(DescribedBase):
    properties = DictType(key_type=text, value_type=property_type)
    pricing = DictType(key_type=text, value_type=property_type)


class InvoiceLine(Base):
    description = text
    price = float
    quantity = float
    sub_total = float
    invoice_id = text


class Invoice(Base):
    identifier = text
    sub_total = float
    tax_percentage = float
    tax_total = float
    total = float


class Subscription(Base):
    billing_day = int
    resource_id = text
    resource_type = text

    plan_id = text
    customer_id = text
    payment_method_id = text


class Usage(Base):
    pass


class PGConfig(Base):
    name = text
    title = text

    properties = DictType(key_type=text, value_type=property_type)


class PaymentMethod(Base):
    name = text
    identifier = text
    expires = text

    customer_id = text
    provider_method_id = text
    provider_config_id = text

    properties = DictType(key_type=text, value_type=property_type)


class Account(Base):
    currency = text
    language = text

    name = text

    def to_db(self):
        values = self.as_dict()
        change_suffixes(values, ['currency', 'language'], shorten=False)
        return values

    @classmethod
    def from_db(cls, values):
        change_suffixes(values, ['currency', 'language'])
        return cls(**values)


class Merchant(Account):
    pass


class Customer(Account):
    def __init__(self, **kw):
        infos = kw.get('contact_info', {})
        kw['contact_info'] = [ContactInfo.from_db(i) for i in infos]
        super(Customer, self).__init__(**kw)

    merchant_id = text
    contact_info = [ContactInfo]
