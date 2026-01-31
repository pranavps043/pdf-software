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
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
import json


# ================================
# Superuser check
# ================================
def superuser_only(user):
    return user.is_superuser

from num2words import num2words


# ================================
# Helper: Amount to words
# ================================
def num_to_words(num):
    try:
        # Split into Dirhams and Fils
        int_part = int(num)
        decimal_part = int(round((num - int_part) * 100))
        
        words = num2words(int_part).replace(',', '') + " Dirhams"
        if decimal_part > 0:
            words += " and " + num2words(decimal_part).replace(',', '') + " Fils"
        
        return words + " Only"
    except Exception:
        return f"{num} AED"


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


# ================================
# Analytics View
# ================================
@login_required
@user_passes_test(superuser_only, login_url="login")
def analytics_view(request):
    # ... (existing analytics_view code)
    # [keeping existing implementation for brevity in thought, but I will write the full view in replacement content]
    # Monthly Revenue for Chart
    last_6_months = []
    today = timezone.now().date()
    for i in range(5, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_name = month_date.strftime('%b %Y')
        next_month = (month_date + timedelta(days=32)).replace(day=1)
    # Determine period and raw dates
    period = request.GET.get('period', 'custom')
    date_from_raw = request.GET.get('date_from', '')
    date_to_raw = request.GET.get('date_to', '')
    
    today = timezone.now().date()
    
    # Filter calculation defaults
    date_from = date_from_raw
    date_to = date_to_raw
    
    if period == 'this_month':
        date_from = today.replace(day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
    elif period == 'last_month':
        last_month = (today.replace(day=1) - timedelta(days=1))
        date_from = last_month.replace(day=1).strftime('%Y-%m-%d')
        date_to = last_month.strftime('%Y-%m-%d')
    elif period == 'last_6_months':
        date_from = (today.replace(day=1) - timedelta(days=150)).replace(day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
    elif period == 'this_year':
        date_from = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')

    # Base filtered queryset for the whole page (Summary, Chart, Clients)
    all_invoices = Invoice.objects.all()
    if date_from:
        all_invoices = all_invoices.filter(date__gte=date_from)
    if date_to:
        all_invoices = all_invoices.filter(date__lte=date_to)

    # Summary Stats (Now based on the active range)
    total_revenue = all_invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    total_vat = float(total_revenue) * 0.05
    total_count = all_invoices.count()
    avg_value = float(total_revenue) / total_count if total_count > 0 else 0

    # Chart data (always 6-month perspective for trend)
    last_6_months_data = []
    for i in range(5, -1, -1):
        m_date = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        m_name = m_date.strftime('%b %Y')
        n_month = (m_date + timedelta(days=32)).replace(day=1)
        m_rev = Invoice.objects.filter(date__gte=m_date, date__lt=n_month).aggregate(Sum('amount'))['amount__sum'] or 0
        last_6_months_data.append({'month': m_name, 'revenue': float(m_rev)})

    # Top clients from the filtered queryset
    top_clients = all_invoices.values('client_name').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')[:5]
    for client in top_clients:
        client['total'] = float(client['total'])

    context = {
        'revenue_data': json.dumps(last_6_months_data),
        'top_clients': top_clients,
        'total_revenue': total_revenue,
        'total_vat': total_vat,
        'total_count': total_count,
        'avg_value': avg_value,
        'date_from': date_from_raw,
        'date_to': date_to_raw,
        'period': period,
    }
    return render(request, 'invoices/analytics.html', context)


import csv
@login_required
@user_passes_test(superuser_only, login_url="login")
def export_analytics_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="business_analytics_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    # Add BOM for Excel compatibility
    response.write('\ufeff')

    writer = csv.writer(response)
    
    # Summary Header
    writer.writerow(['BUSINESS ANALYTICS SUMMARY'])
    writer.writerow(['Generated At', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    
    # Period filters
    period = request.GET.get('period', 'custom')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    today = timezone.now().date()
    
    if period == 'this_month':
        date_from = today.replace(day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
    elif period == 'last_month':
        last_month = (today.replace(day=1) - timedelta(days=1))
        date_from = last_month.replace(day=1).strftime('%Y-%m-%d')
        date_to = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
    elif period == 'last_6_months':
        date_from = (today.replace(day=1) - timedelta(days=150)).replace(day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
    elif period == 'this_year':
        date_from = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
        
    if date_from or date_to:
        writer.writerow(['Filters', f'Period: {period} | From: {date_from or "All"} | To: {date_to or "All"}'])
    
    writer.writerow([])
    
    all_invoices = Invoice.objects.all().order_by('-date')
    if date_from:
        all_invoices = all_invoices.filter(date__gte=date_from)
    if date_to:
        all_invoices = all_invoices.filter(date__lte=date_to)
    total_revenue = all_invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    total_vat = float(total_revenue) * 0.05
    
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Revenue (AED)', f"{total_revenue:.2f}"])
    writer.writerow(['Total VAT Collected (AED)', f"{total_vat:.2f}"])
    writer.writerow(['Total Quotations', all_invoices.count()])
    writer.writerow(['Average Value (AED)', f"{(float(total_revenue)/all_invoices.count() if all_invoices.count() > 0 else 0):.2f}"])
    writer.writerow([])
    
    # Detailed Data
    writer.writerow(['DETAILED INVOICE DATA'])
    writer.writerow(['Date', 'Invoice No', 'Client Name', 'Reference', 'Amount (AED)', 'VAT (5%)', 'Total (AED)'])
    
    for invoice in all_invoices:
        amt = float(invoice.amount)
        vat = amt * 0.05
        writer.writerow([
            invoice.date.strftime('%d/%m/%Y'),
            invoice.invoice_number,
            invoice.client_name,
            invoice.reference_no,
            f"{amt:.2f}",
            f"{vat:.2f}",
            f"{(amt + vat):.2f}"
        ])
        
    return response

