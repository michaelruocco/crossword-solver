import ipaddress

IpAddress = ipaddress.IPv4Address | ipaddress.IPv6Address


def is_public_address(address: IpAddress) -> bool:
    # An IPv4 address wrapped in IPv6 is judged as the IPv4 address it carries.
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        address = address.ipv4_mapped
    return address.is_global
