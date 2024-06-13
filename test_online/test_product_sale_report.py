import datetime

from fiken_py.models import ProductSalesReport, Sale, Invoice
from fiken_py.shared_types import OrderLine, InvoiceLine


def test_product_sale_report(
    unique_id, generic_product, generic_contact, generic_bank_account
):
    reports = ProductSalesReport.get_report_for_timeframe(
        datetime.date.today(),
        datetime.date.today(),
    )

    sold = 0

    # find sold

    for report in reports:
        assert report.product is not None

        if report.product == generic_product:
            sold = report.sold.count

    # create a sale
    new_sale = Invoice(
        lines=[
            InvoiceLine(
                productId=generic_product.productId,
                quantity=1,
                unitPrice=100,
            )
        ],
        issueDate=datetime.date.today(),
        dueDate=datetime.date.today(),
        customer=generic_contact,
        cash=True,
    )

    new_sale.save(
        bankAccountCode=generic_bank_account.accountCode,
        paymentAccount=generic_bank_account.accountCode,
    )

    reports_new = ProductSalesReport.get_report_for_timeframe(
        datetime.date.today(),
        datetime.date.today(),
    )

    for report in reports_new:
        if report.product == generic_product:
            assert report.sold.count == sold + 1
            break
