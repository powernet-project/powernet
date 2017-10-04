from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def home_data_view(request):
    h1 = {
        'home_id': 1,
        'home_name': 'My Home One',
        'home_load': '1 kW',
        'home_devices': [{
                'device_id': 123,
                'device_name': 'refrigerator',
                'device_load': '0.1 mW',
                'device_status': 'ON'
            },
            {
                'device_id': 124,
                'device_name': 'storage',
                'device_load': '0.1 mW',
                'device_status': 'OFF'
            }
        ]
    }

    h2 = {
        'home_id': 2,
        'home_name': 'My Home Two',
        'home_load': '10 kW',
        'home_devices': [{
                'device_id': 223,
                'device_name': 'refrigerator',
                'device_load': '0.1 mW',
                'device_status': 'ON'
            },
            {
                'device_id': 224,
                'device_name': 'storage',
                'device_load': '0.1 mW',
                'device_status': 'OFF'
            }
        ]
    }

    return Response([h1, h2])

