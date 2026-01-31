
import os
import django
from django.test import RequestFactory
from django.urls import reverse
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_system.settings')
django.setup()

try:
    from invoices.models import Invoice
    from invoices.views import invoice_list
    
    count = Invoice.objects.count()
    print(f"Invoice count: {count}")
    
    if count > 0:
        inv = Invoice.objects.first()
        print(f"First invoice ID: {inv.id}")
        print(f"Update URL: {reverse('invoice_update', args=[inv.id])}")
        print(f"Delete URL: {reverse('invoice_delete', args=[inv.id])}")

    factory = RequestFactory()
    request = factory.get('/list/')
    response = invoice_list(request)
    
    if response.status_code == 200:
        print("Render successful (200)")
        # Force render content to trigger template errors
        print(f"Content length: {len(response.content)}")
    else:
        print(f"Response status: {response.status_code}")

except Exception as e:
    traceback.print_exc()
