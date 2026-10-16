import ipaddress

import pytest

from crossword_solver_domain_use_case.address_policy import is_public_address


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        ("93.184.216.34", True),
        ("2606:2800:220:1:248:1893:25c8:1946", True),
        ("::ffff:93.184.216.34", True),
        ("127.0.0.1", False),
        ("10.1.2.3", False),
        ("172.16.0.1", False),
        ("192.168.0.1", False),
        ("169.254.169.254", False),
        ("100.64.0.1", False),
        ("0.0.0.0", False),
        ("::1", False),
        ("fe80::1", False),
        ("fc00::1", False),
        ("::ffff:10.0.0.1", False),
        ("::ffff:127.0.0.1", False),
    ],
)
def test_is_public_address(address, expected):
    assert is_public_address(ipaddress.ip_address(address)) is expected
