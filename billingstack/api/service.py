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
#
# Copied: Moniker
from oslo.config import cfg
from paste import deploy

from billingstack.openstack.common import log as logging
from billingstack.openstack.common import wsgi
from billingstack import exceptions
from billingstack import utils
#from billingstack import policy


cfg.CONF.import_opt('state_path', 'billingstack.paths')


LOG = logging.getLogger(__name__)


class Service(wsgi.Service):
    def __init__(self, backlog=128, threads=1000):

        api_paste_config = cfg.CONF['service:api'].api_paste_config
        config_paths = utils.find_config(api_paste_config)

        if len(config_paths) == 0:
            msg = 'Unable to determine appropriate api-paste-config file'
            raise exceptions.ConfigurationError(msg)

        LOG.info('Using api-paste-config found at: %s' % config_paths[0])

        #policy.init_policy()

        application = deploy.loadapp("config:%s" % config_paths[0],
                                     name='bs_api')

        super(Service, self).__init__(application=application,
                                      host=cfg.CONF['service:api'].api_listen,
                                      port=cfg.CONF['service:api'].api_port,
                                      backlog=backlog,
                                      threads=threads)