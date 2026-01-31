
import os
import django
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_system.settings')
django.setup()

try:
    print(f"Update URL: {reverse('invoice_update', args=[1])}")
    print(f"Delete URL: {reverse('invoice_delete', args=[1])}")
    print("URL resolution successful")
except Exception as e:
    print(f"URL resolution failed: {e}")
