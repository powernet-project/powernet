import unittest
from main.api_network import NetworkInterface


class TestApiNetwork(unittest.TestCase):

    def test_invalid_token_in_request(self):
        # initialize the Network API class
        api = NetworkInterface('FAKE_TOKEN')
        
        # ensure that an error is raised when an invalid token is given
        with self.assertRaises(KeyError):
            api.get_device_status()

if __name__ == '__main__':
    unittest.main()