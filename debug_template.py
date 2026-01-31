
import os
import django
from django.template.loader import render_to_string
from django.test import RequestFactory
from invoices.models import Invoice

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_system.settings')
django.setup()

try:
    factory = RequestFactory()
    request = factory.get('/list/')
    # Need to mock paginator or just pass context manually to test template syntax
    from invoices.views import invoice_list
    response = invoice_list(request)
    print("Render successful (status code):", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
