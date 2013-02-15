# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
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
"""Base classes for API tests.
"""

import os

from pecan import set_config
from pecan.testing import load_test_app

from billingstack.openstack.common import log
from billingstack.openstack.common import jsonutils as json
from billingstack.tests import base


LOG = log.getLogger(__name__)


class FunctionalTest(base.TestCase):
    """
    Used for functional tests of Pecan controllers where you need to
    test your literal application and its integration with the
    framework.
    """

    PATH_PREFIX = ''

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.app = self._make_app()

    def _make_app(self, enable_acl=False):
        # Determine where we are so we can set up paths in the config
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                '..',
                                                )
                                   )

        self.config = {
            'app': {
                'root': 'billingstack.api.controllers.root.RootController',
                'modules': ['billingstack.api'],
                'static_root': '%s/public' % root_dir,
                'template_path': '%s/billingstack/api/templates' % root_dir,
                'enable_acl': enable_acl,
            },

            'logging': {
                'loggers': {
                    'root': {'level': 'INFO', 'handlers': ['console']},
                    'wsme': {'level': 'INFO', 'handlers': ['console']},
                    'billingstack': {'level': 'DEBUG',
                                   'handlers': ['console'],
                                   },
                },
                'handlers': {
                    'console': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'simple'
                    }
                },
                'formatters': {
                    'simple': {
                        'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                                   '[%(threadName)s] %(message)s')
                    }
                },
            },
        }

        return load_test_app(self.config)

    def tearDown(self):
        super(FunctionalTest, self).tearDown()
        set_config({}, overwrite=True)

    def make_path(self, path):
        if not path.startswith('/'):
            path = '/' + path
        return self.PATH_PREFIX + path

    def _query(self, queries):
        query_params = {'q.field': [],
                        'q.value': [],
                        'q.op': [],
                        }
        for query in queries:
            for name in ['field', 'op', 'value']:
                query_params['q.%s' % name].append(query.get(name, ''))
        return query_params

    def _params(self, params, queries):
        all_params = {}
        all_params.update(params)
        if queries:
            all_params.update(self._query(queries))
        return all_params

    def get(self, path, headers=None,
            q=[], status_code=200, **params):
        path = self.make_path(path)
        all_params = self._params(params, q)

        LOG.debug('GET: %s %r', path, all_params)

        response = self.app.get(path,
                                params=all_params,
                                headers=headers)

        LOG.debug('GOT RESPONSE: %s', response)

        self.assertEqual(response.status_code, status_code)

        return response

    def post(self, path, data, headers=None, content_type="application/json",
             q=[], status_code=200):
        path = self.make_path(path)

        LOG.debug('POST: %s %s', path, data)

        content = json.dumps(data)
        response = self.app.post(
            path,
            content,
            content_type=content_type,
            headers=headers)

        LOG.debug('POST RESPONSE: %r' % response.body)

        self.assertEqual(response.status_code, status_code)

        return response

    def put(self, path, data, headers=None, content_type="application/json",
            q=[], status_code=200, **params):
        path = self.make_path(path)

        LOG.debug('PUT: %s %s', path, data)

        content = json.dumps(data)
        response = self.app.put(
            path,
            content,
            content_type=content_type,
            headers=headers)

        self.assertEqual(response.status_code, status_code)

        LOG.debug('PUT RESPONSE: %r' % response.body)

        return response

    def delete(self, path, status_code=200, headers=None, q=[], **params):
        path = self.make_path(path)
        all_params = self._params(params, q)

        LOG.debug('DELETE: %s %r', path, all_params)

        response = self.app.delete(path, params=all_params)

        LOG.debug('DELETE RESPONSE: %r' % response.body)

        self.assertEqual(response.status_code, status_code)

        return response