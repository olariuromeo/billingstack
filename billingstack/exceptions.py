# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
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


class Base(Exception):
    pass


class NotImplemented(Base, NotImplementedError):
    pass


class ConfigurationError(Base):
    pass


class InvalidObject(Base):
    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop('errors', None)
        super(InvalidObject, self).__init__(*args, **kwargs)


class BadRequest(Base):
    pass


class Forbidden(Base):
    pass


class InvalidSortKey(Base):
    pass


class InvalidQueryField(Base):
    pass


class InvalidOperator(Base):
    pass


class Duplicate(Base):
    pass


class NotFound(Base):
    pass
