
import os
import django
from django.test import RequestFactory
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_system.settings')
django.setup()

try:
    from invoices.views import invoice_list
    
    factory = RequestFactory()
    request = factory.get('/list/')
    
    # We might need to mock get_object_or_404 or other things if they were used, 
    # but invoice_list relies on Invoice.objects.all(), which should work if DB is accessible.
    
    response = invoice_list(request)
    if response.status_code == 200:
        print("Render successful")
    else:
        print(f"Response status: {response.status_code}")
        
except Exception as e:
    traceback.print_exc()
