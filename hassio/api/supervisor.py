"""Init file for HassIO supervisor rest api."""
import logging

import voluptuous as vol

from .util import api_process, api_process_hostcontroll, api_validate
from ..const import (
    ATTR_ADDONS, ATTR_VERSION, ATTR_CURRENT, ATTR_BETA, HASSIO_VERSION)

_LOGGER = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema({
    # pylint: disable=no-value-for-parameter
    vol.Optional(ATTR_BETA): vol.Boolean(),
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APISupervisor(object):
    """Handle rest api for supervisor functions."""

    def __init__(self, config, loop, host_controll, addons):
        """Initialize supervisor rest api part."""
        self.config = config
        self.loop = loop
        self.host_controll = host_controll
        self.addons = addons

    @api_process
    async def ping(self, request):
        """Return ok for signal that the api is ready."""
        return True

    @api_process
    async def info(self, request):
        """Return host information."""
        info = {
            ATTR_VERSION: HASSIO_VERSION,
            ATTR_CURRENT: self.config.current_hassio,
            ATTR_BETA: self.config.upstream_beta,
            ATTR_ADDONS: self.addons.list,
        }
        return info

    @api_process
    async def options(self, request):
        """Set supervisor options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_BETA in body:
            self.config.upstream_beta = body[ATTR_BETA]

        return self.config.save()

    @api_process_hostcontroll
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.config.current_hassio)

        if version == HASSIO_VERSION:
            raise RuntimeError("Version is already in use")

        return await self.host_controll.supervisor_update(version=version)