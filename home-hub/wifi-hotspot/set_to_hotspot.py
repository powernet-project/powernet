from wificonnector.wifi_control import add_dhcpcd_conf, start_hostapd, start_dnsmasq, restart_dhcpcd


def set_to_hotspot():
    add_dhcpcd_conf()
    start_hostapd()
    start_dnsmasq()
    restart_dhcpcd()
