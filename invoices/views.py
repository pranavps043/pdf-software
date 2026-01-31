from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Invoice
from .forms import InvoiceForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q


# ================================
# Superuser check
# ================================
def superuser_only(user):
    return user.is_superuser


# ================================
# Helper: Amount to words
# ================================
def num_to_words(num):
    return f"{num} (amount in words)"


# ================================
# Create Invoice / Quotation
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def invoice_create(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return redirect(f"{reverse('invoice_create')}?created_id={instance.id}")
    else:
        form = InvoiceForm()
    
    created_invoice = None
    created_id = request.GET.get('created_id')
    if created_id:
        created_invoice = Invoice.objects.filter(pk=created_id).first()

    return render(request, "invoices/create_invoice.html", {
        "form": form,
        "title": "Create Quotation",
        "created_invoice": created_invoice
    })


# ================================
# Invoice List (Search + Filter + Pagination)
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def invoice_list(request):
    invoices_qs = Invoice.objects.all().order_by("-created_at")

    # Search
    search_query = request.GET.get("search", "")
    if search_query:
        invoices_qs = invoices_qs.filter(
            Q(client_name__icontains=search_query) |
            Q(invoice_number__icontains=search_query) |
            Q(reference_no__icontains=search_query)
        )

    # Date filter
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if date_from:
        invoices_qs = invoices_qs.filter(date__gte=date_from)
    if date_to:
        invoices_qs = invoices_qs.filter(date__lte=date_to)

    # Pagination
    paginator = Paginator(invoices_qs, 10)
    page_number = request.GET.get("page")
    invoices = paginator.get_page(page_number)

    context = {
        "invoices": invoices,
        "search_query": search_query,
        "date_from": date_from,
        "date_to": date_to,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "invoices/partials/invoice_table_partial.html", context)

    return render(request, "invoices/invoice_list.html", context)


# ================================
# Invoice PDF
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def generate_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    vat_rate = Decimal("0.05")
    vat_amount = invoice.amount * vat_rate
    total_with_vat = invoice.amount + vat_amount

    context = {
        "invoice": invoice,
        "vat_amount": round(vat_amount, 2),
        "total_with_vat": round(total_with_vat, 2),
        "amount_in_words": num_to_words(total_with_vat),
    }

    template = get_template("invoices/pdf_template.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="invoice_{invoice.reference_no}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error")

    return response


# ================================
# Quotation PDF
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def generate_quotation(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    vat_rate = Decimal("0.05")
    vat_amount = invoice.amount * vat_rate
    total_with_vat = invoice.amount + vat_amount

    context = {
        "invoice": invoice,
        "vat_amount": round(vat_amount, 2),
        "total_with_vat": round(total_with_vat, 2),
        "amount_in_words": num_to_words(total_with_vat),
    }

    template = get_template("invoices/quotation_template.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="quotation_{invoice.reference_no}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error")

    return response


# ================================
# Update Invoice
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect("invoice_list")
    else:
        form = InvoiceForm(instance=invoice)

    return render(request, "invoices/create_invoice.html", {
        "form": form,
        "title": "Edit Quotation"
    })


# ================================
# Delete Invoice
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == "POST":
        invoice.delete()
        return redirect("invoice_list")

    return render(request, "invoices/invoice_confirm_delete.html", {
        "invoice": invoice
    })
