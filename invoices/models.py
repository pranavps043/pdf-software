from django.db import models

class Invoice(models.Model):
    invoice_number = models.PositiveIntegerField(unique=True, editable=False, null=True, blank=True)
    client_name = models.CharField(max_length=255)
    reference_no = models.CharField(max_length=100)
    date = models.DateField()
    subject = models.CharField(max_length=255)
    address = models.TextField()
    mobile_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    work_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Get the last invoice number, or start from 9999 (so first one is 10000)
            last_invoice = Invoice.objects.filter(invoice_number__isnull=False).order_by('invoice_number').last()
            if last_invoice:
                self.invoice_number = last_invoice.invoice_number + 1
            else:
                self.invoice_number = 10000
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_no} - {self.client_name}"
