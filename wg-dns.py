import socket, os, sys, re
from os.path import exists
from typing import List, Dict

def read_wg_config(config_content:str):
    return_value = {}
    current_interface = None
    current_data = {}
    def push_current():
        nonlocal current_interface
        nonlocal current_data
        if current_interface:
            if current_interface in return_value:
                return_value[current_interface].append(current_data)
            else:
                return_value[current_interface] = [current_data]
    for line in config_content.split('\n'):
        match_result = re.match(r'\[([a-zA-Z0-9]+)\]', line)
        if match_result:
            push_current()
            current_interface = match_result[1]
            current_data = {}
        match_result = re.match(r'([^\=]+?)(\s*)=(\s*)(.+)', line)
        if match_result:
            current_data[match_result.group(1)] = match_result.group(4)
    push_current()
    return return_value

def refresh_peer_ddns(interface:str, peers:List[Dict]):
    for peer in peers:
        if 'EndPoint' in peer and 'PublicKey' in peer:
            domain = peer['EndPoint'].split(':')[0]
            current_ip = socket.gethostbyname(domain)
            new_endpoint = peer['EndPoint'].replace(domain, current_ip)
            exec_shell = 'wg set {0} peer {1} endpoint {2}'.format(interface, peer['PublicKey'], new_endpoint)
            os.system(exec_shell)
            print('success to update peer: {}'.format(exec_shell))

def main():
    if len(sys.argv) < 1:
        print('please input wireguard interface name')
        exit(1)
    interface = sys.argv[1]
    conf_path = '/etc/wireguard/{}.conf'.format(interface)
    if not exists(conf_path):
        print('{} configuration is not exists'.format(conf_path))
        exit(1)
    file_content = open(conf_path, 'r').read()
    wg_config = read_wg_config(file_content)
    if 'Peer' not in wg_config:
        print('{} does not has Peer'.format(conf_path))
    refresh_peer_ddns(interface, wg_config['Peer'])

if __name__ == '__main__':
    main()