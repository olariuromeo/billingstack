from oslo.config import cfg

cfg.CONF.register_group(cfg.OptGroup(
    name='service:collector', title="Configuration for collector Service"
))

cfg.CONF.register_opts([
    cfg.IntOpt('workers', default=None,
               help='Number of worker processes to spawn'),
    cfg.StrOpt('storage-driver', default='sqlalchemy',
               help='The storage driver to use'),
], group='service:collector')