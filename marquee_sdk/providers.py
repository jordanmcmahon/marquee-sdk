from urllib     import urlencode

import requests
import socket

class DigitalOceanClient(object):
    def __init__(self, access_token):
        self.access_token   =  access_token
        self.endpoint       = 'https://api.digitalocean.com/v2/{action}?params={params}'
        self.headers        = {'Authorization': 'Bearer {0}'.format(self.access_token)}

    def get(self, action, params={}):
        url = self.endpoint.format(action=action, params=urlencode(params))
        r   = requests.get(url, headers=self.headers).json()
        return r

    def post(self, action, data={}):
        url = self.endpoint.format(action=action)
        r   = requests.post(url, data=data, headers=self.headers).json()
        print r
        return r

    def list_keys(self):
        return self.get('account/keys')['ssh_keys']

    def create_key(self, name, public_key):
        data = {
            'name'       : socket.gethostname(),
            'public_key' : public_key,
        }
        return self.post('account/keys', data=data)['ssh_key']

    def list_droplets(self):
        return self.get('droplets')['droplets']

    def create_droplet(self, name, region, size, image, ssh_keys=[], backups=False, ipv6=False, private_networking=False):
        data = {
            'name'              : name,
            'region'            : region,
            'size'              : size,
            'image'             : image,
            'ssh_keys'          : ssh_keys,
            'backups'           : backups,
            'ipv6'              : ipv6,
            'private_networking': private_networking,
        }
        return self.post('droplets', data=data)['droplet']

    def droplet_actions(self, droplet_id):
        action = 'droplets/{0}/actions'.format(droplet_id)
        return self.get(action=action)['actions']
