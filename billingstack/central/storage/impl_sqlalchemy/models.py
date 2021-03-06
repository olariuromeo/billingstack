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
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from billingstack import utils
from billingstack.openstack.common import log as logging
from billingstack.sqlalchemy.types import JSON, UUID
from billingstack.sqlalchemy.model_base import (
    ModelBase, BaseMixin, PropertyMixin)

LOG = logging.getLogger(__name__)


BASE = declarative_base(cls=ModelBase)


class Currency(BASE):
    """
    Allowed currency
    """
    name = Column(Unicode(10), nullable=False, primary_key=True)
    title = Column(Unicode(100), nullable=False)


class Language(BASE):
    """
    A Language
    """
    name = Column(Unicode(10), nullable=False, primary_key=True)
    title = Column(Unicode(100), nullable=False)


class ContactInfo(BASE, BaseMixin):
    """
    Contact Information about an entity like a User, Customer etc...
    """

    @declared_attr
    def __mapper_args__(cls):
        name = unicode(utils.capital_to_underscore(cls.__name__))
        return {"polymorphic_on": "info_type", "polymorphic_identity": name}

    info_type = Column(Unicode(20), nullable=False)

    first_name = Column(Unicode(100))
    last_name = Column(Unicode(100))
    company = Column(Unicode(100))
    address1 = Column(Unicode(255))
    address2 = Column(Unicode(255))
    address3 = Column(Unicode(255))
    locality = Column(Unicode(60))
    region = Column(Unicode(60))
    country_name = Column(Unicode(100))
    postal_code = Column(Unicode(40))

    phone = Column(Unicode(100))
    email = Column(Unicode(100))
    website = Column(Unicode(100))


class CustomerInfo(ContactInfo):
    id = Column(UUID, ForeignKey("contact_info.id",
                                 onupdate='CASCADE', ondelete='CASCADE'),
                primary_key=True)

    customer_id = Column(UUID, ForeignKey('customer.id'), nullable=False)


class Merchant(BASE, BaseMixin):
    """
    A Merchant is like a Account in Recurly
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(60))

    customers = relationship('Customer', backref='merchant')

    plans = relationship('Plan', backref='merchant')
    products = relationship('Product', backref='merchant')

    currency = relationship('Currency', uselist=False, backref='merchants')
    currency_name = Column(Unicode(10), ForeignKey('currency.name'),
                           nullable=False)

    language = relationship('Language', uselist=False, backref='merchants')
    language_name = Column(Unicode(10), ForeignKey('language.name'),
                           nullable=False)


class Customer(BASE, BaseMixin):
    """
    A Customer is linked to a Merchant and can have Users related to it
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(60))

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)

    contact_info = relationship(
        'CustomerInfo',
        backref='customer',
        primaryjoin='Customer.id == CustomerInfo.customer_id',
        lazy='joined')

    default_info = relationship(
        'CustomerInfo',
        primaryjoin='Customer.default_info_id == CustomerInfo.id',
        uselist=False,
        post_update=True)
    default_info_id = Column(
        UUID,
        ForeignKey('customer_info.id', use_alter=True,
                   onupdate='CASCADE', name='default_info'))

    currency = relationship('Currency', uselist=False, backref='customers')
    currency_name = Column(Unicode(10), ForeignKey('currency.name'))

    language = relationship('Language', uselist=False, backref='customers')
    language_name = Column(Unicode(10), ForeignKey('language.name'))


class Plan(BASE, BaseMixin):
    """
    A Product collection like a "Virtual Web Cluster" with 10 servers
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))
    #provider = Column(Unicode(255), nullable=False)

    plan_items = relationship('PlanItem', backref='plan')

    merchant_id = Column(UUID, ForeignKey('merchant.id',
                         ondelete='CASCADE'), nullable=False)


class PlanProperty(BASE, PropertyMixin):
    __table_args__ = (UniqueConstraint('name', 'plan_id', name='plan'),)

    plan = relationship('Plan', backref='properties', lazy='joined')
    plan_id = Column(
        UUID,
        ForeignKey('plan.id',
                   ondelete='CASCADE',
                   onupdate='CASCADE'))


class PlanItem(BASE, BaseMixin):
    __table_args__ = (UniqueConstraint('plan_id', 'product_id', name='item'),)

    title = Column(Unicode(100))
    description = Column(Unicode(255))

    pricing = Column(JSON)

    plan_id = Column(UUID, ForeignKey('plan.id', ondelete='CASCADE'),
                     onupdate='CASCADE', primary_key=True)

    product = relationship('Product', backref='plan_items', uselist=False)
    product_id = Column(UUID, ForeignKey('product.id', onupdate='CASCADE'),
                        primary_key=True)


class Product(BASE, BaseMixin):
    """
    A sellable Product, like vCPU hours, bandwidth units
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    pricing = Column(JSON)

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)


class ProductProperty(BASE, PropertyMixin):
    """
    A Metadata row for something like Product or PlanItem
    """
    __table_args__ = (UniqueConstraint('name', 'product_id', name='product'),)

    product = relationship('Product', backref='properties', lazy='joined')
    product_id = Column(
        UUID,
        ForeignKey('product.id',
                   ondelete='CASCADE',
                   onupdate='CASCADE'))


class Subscription(BASE, BaseMixin):
    """
    The thing that ties together stuff that is to be billed

    In other words a Plan which is a collection of Products or a Product.
    """
    billing_day = Column(Integer)

    resource_id = Column(Unicode(255), nullable=False)
    resource_type = Column(Unicode(255), nullable=True)

    plan = relationship('Plan', backref='subscriptions', uselist=False)
    plan_id = Column(UUID, ForeignKey('plan.id', ondelete='CASCADE'),
                     nullable=False)

    customer = relationship('Customer', backref='subscriptions')
    customer_id = Column(UUID, ForeignKey('customer.id', ondelete='CASCADE'),
                         nullable=False)

    payment_method_id = Column(UUID)
