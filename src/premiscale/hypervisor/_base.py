"""
Provide methods to interact with the Libvirt API.
"""


from __future__ import annotations

import libvirt as lv
import logging

from typing import Any
from libvirt import libvirtError
from ipaddress import IPv4Address


log = logging.getLogger(__name__)


class Libvirt:
    """
    Connect to hosts and provide an interface for interacting with VMs on them.

    Args:
        host (IPv4Address): IP address of the host to connect to.
        user (str): Username to authenticate with (if using SSH).
        hypervisor_type (str): Type of hypervisor to connect to. Defaults to 'qemu'. Can be either 'qemu' or 'lxc'.
        auth_type (str): Type of authentication to use. Defaults to 'ssh'. Can be either 'ssh' or 'tls'.
    """
    def __init__(self, host: IPv4Address, user: str, hypervisor_type: str, auth_type: str) -> None:
        self.host = host
        self.user = user
        self.hypervisor_type = hypervisor_type
        self.auth_type = auth_type

        if auth_type == 'ssh':
            self.connection_string = f'{hypervisor_type}+ssh://{user}@{host}/system'
        elif auth_type == 'tls':
            self.connection_string = f'{hypervisor_type}+tls://{host}/system'

    def __enter__(self) -> Libvirt | None:
        return self.open()

    def __exit__(self, *args: Any) -> None:
        self.close()

    def open(self) -> Libvirt | None:
        """
        Open a connection to the Libvirt hypervisor.
        """
        try:
            self.connection = lv.open(self.connection_string)
            log.info(f'Connected to host at {self.connection_string}')
        except libvirtError as e:
            log.error(f'Failed to connect to host at {self.connection_string}: {e}')
            return None

        return self

    def close(self) -> None:
        """
        Close the connection with the Libvirt hypervisor.
        """
        self.connection.close()