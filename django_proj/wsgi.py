import os
import tempfile

import matplotlib as mpl
mpl.use('Agg')

os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artoflife.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
