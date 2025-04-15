#!/usr/bin/env python3
# Copyright 2025 Canonical
# See LICENSE file for licensing details.

"""Message of the Day charm.

Charm for deploying an apache2 server that servers the Ubuntu Message of the Day.
"""

import logging

import ops

logger = logging.getLogger(__name__)

VALID_LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]


class MotdK8SCharm(ops.CharmBase):
    """Main operator for the Ubuntu Message of the Day service."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on["httpbin"].pebble_ready, self._on_httpbin_pebble_ready)

    def _on_httpbin_pebble_ready(self, event: ops.PebbleReadyEvent):
        """Deploys the Pebble layer via the Pebble API when Pebble is ready."""
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Add initial Pebble config layer using the Pebble API
        container.add_layer("httpbin", self._pebble_layer, combine=True)
        # Make Pebble reevaluate its plan, ensuring any services are started if enabled.
        container.replan()
        # Set Charm status to Active.
        self.unit.status = ops.ActiveStatus()

    @property
    def _pebble_layer(self) -> ops.pebble.LayerDict:
        """Returns a dictionary representing the MOTD Pebble layer."""
        return {
            "summary": "MOTD layer",
            "description": "pebble config layer for Ubuntu MOTD",
            "services": {
                "motd": {
                    "override": "replace",
                    "summary": "motd",
                    "command": "/usr/sbin/apache2ctl -D FOREGROUND",
                    "startup": "enabled",
                }
            },
        }


if __name__ == "__main__":  # pragma: nocover
    ops.main(MotdK8SCharm)
