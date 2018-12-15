from subprocess import call
import re


def add_dhcpcd_conf():
    with open("/etc/dhcpcd.conf", "r+") as f:
        original = f.readlines()
        location = if_dhcpcd_conf_exist(original)
        if len(location) == 0:
            f.writelines(["\n", "# create hot spot\n", "interface wlan0\n", "    static ip_address=192.168.4.1/24\n",
                          "    nohook wpa_supplicant\n", "# create hot spot end\n"])


def if_dhcpcd_conf_exist(text):
    location = []
    for line, content in enumerate(text):
        if "# create hot spot" in content:
            location.append(line)
    return location


def delete_dhcpcd_conf():
    with open("/etc/dhcpcd.conf", "r") as fr:
        original = fr.readlines()
        location = if_dhcpcd_conf_exist(original)
        if len(location) == 2:
            with open("/etc/dhcpcd.conf", "w") as fw:
                fw.writelines(original[:location[0]])
                fw.writelines(original[location[1] + 1:])


def add_wifi_conf(ssid, psk):
    path = "/etc/wpa_supplicant/wpa_supplicant.conf"
    with open(path, "r+") as f:
        conf = "\nnetwork={\n\tssid=\"%s\"\n\tpsk=\"%s\"\n\tkey_mgmt=WPA-PSK\n}" % (ssid, psk)
        original = "".join(f.readlines())
        if "ssid=\"%s\"" % ssid not in original:
            f.write(conf)
        else:  # SSID exsited, overide it
            result = re.findall("network={\s*ssid=\"%s\"[^}]*}" % ssid, original)
            if len(result) != 0:
                index = original.find(result[0])
                with open(path, "w") as fw:
                    fw.write(original[:index] + conf + original[index + len(result[0]):])


def stop_hostapd():
    call(["systemctl", "stop", "hostapd"])


def disable_hostapd():
    call(["systemctl", "disable", "hostapd"])


def restart_dhcpcd():
    call(["systemctl", "restart", "dhcpcd"])


def start_hostapd():
    call(["systemctl", "start", "hostapd"])


def start_dnsmasq():
    call(["systemctl", "start", "dnsmasq"])