"""
Celery background tasks for billing operations.

Handles invoice generation and email notifications.
"""

from decimal import Decimal

from celery import shared_task
from django.utils import timezone


@shared_task(queue="normal")
def generate_invoice(trip_id):
    """
    Generate invoice for a completed trip.

    Args:
        trip_id: ID of the completed trip

    Returns:
        Invoice ID if successful, error message otherwise
    """
    from billing.models import Invoice
    from trips.models import Trip

    try:
        trip = Trip.objects.select_related("patient", "driver", "vehicle").get(id=trip_id)

        # Check if invoice already exists
        if Invoice.objects.filter(trip_id=trip_id).exists():
            return f"Invoice already exists for trip {trip_id}"

        # Calculate invoice amount (placeholder logic - customize as needed)
        base_rate = Decimal("50.00")  # Base trip rate
        distance_km = Decimal("10.0")  # TODO: Calculate from GPS data
        rate_per_km = Decimal("2.50")

        subtotal = base_rate + (distance_km * rate_per_km)
        tax_rate = Decimal("0.15")  # 15% tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount

        # Create invoice
        invoice = Invoice.objects.create(
            trip=trip,
            patient=trip.patient,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=30),
            subtotal=subtotal,
            tax=tax_amount,
            total_amount=total_amount,
            status="pending",
            notes=f"Invoice for trip #{trip_id}",
        )

        # Send invoice email
        send_invoice_email.delay(invoice.id)

        return f"Invoice {invoice.id} generated for trip {trip_id}"

    except Trip.DoesNotExist:
        return f"Trip {trip_id} not found"
    except Exception as e:
        return f"Error generating invoice for trip {trip_id}: {str(e)}"


@shared_task(queue="low_priority")
def send_invoice_email(invoice_id):
    """
    Send invoice email to patient.

    Args:
        invoice_id: Invoice ID

    Returns:
        Success or error message
    """
    from billing.models import Invoice

    try:
        invoice = Invoice.objects.select_related("patient", "trip").get(id=invoice_id)

        if not invoice.patient or not invoice.patient.email:
            return f"No email address for invoice {invoice_id}"

        # TODO: Implement actual email sending
        # For now, just log the action
        # Email subject for reference
        _ = f"Invoice #{invoice.invoice_number} - ATW Transportation"  # noqa: F841
        recipient = invoice.patient.email

        # Placeholder - replace with actual email service
        # send_email(
        #     subject=subject,
        #     recipient=recipient,
        #     template="invoice_email.html",
        #     context={"invoice": invoice}
        # )

        return f"Invoice email sent to {recipient} for invoice {invoice_id}"

    except Invoice.DoesNotExist:
        return f"Invoice {invoice_id} not found"
    except Exception as e:
        return f"Error sending invoice email: {str(e)}"


@shared_task(queue="normal")
def process_overdue_invoices():
    """
    Periodic task to process overdue invoices.

    Sends reminder emails and updates invoice status.
    """
    from billing.models import Invoice

    today = timezone.now().date()

    # Find overdue unpaid invoices
    overdue_invoices = Invoice.objects.filter(
        status="pending",
        due_date__lt=today,
    )

    processed_count = 0
    for invoice in overdue_invoices:
        # Update status to overdue
        invoice.status = "overdue"
        invoice.save(update_fields=["status"])

        # Send reminder email
        if invoice.patient and invoice.patient.email:
            # TODO: Implement overdue reminder email
            processed_count += 1

    return f"Processed {processed_count} overdue invoices"
