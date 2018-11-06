import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.base")
import django
django.setup()

from app.models import MatlabFiles
import scipy.io as sio
import json
import numpy as np

# convert the Matlab content to JSON format
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    content = sio.loadmat(sys.argv[1])
    name = sys.argv[1].split('/')[-1]
    lines = json.dumps(content, cls = NumpyEncoder)
    f = MatlabFiles.objects.create(filename = name, content = lines)
