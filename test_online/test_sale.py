import datetime

from fiken_py.models import (
    SaleDraft,
    Contact,
    BankAccount,
    Sale,
    PaymentSale,
)
from fiken_py.shared_enums import SaleKind
from fiken_py.shared_types import OrderLine
from test_online import shared_tests, sample_object_factory


def test_sale_manual(
    unique_id: str, generic_contact: Contact, generic_bank_account: BankAccount
):
    sale_request = sample_object_factory.sale(unique_id, generic_contact)

    sale: Sale = sale_request.save()

    assert sale is not None
    assert sale.saleId is not None

    assert len(sale.salePayments) == 0

    payment: PaymentSale = PaymentSale(
        amount=1250,
        account=generic_bank_account.accountCode,
        date=datetime.date.today(),
    )
    sale.add_payment(payment)

    sale._refresh_object()

    assert len(sale.salePayments) == 1
    assert sale.salePayments[0].amount == 1250


def test_sale_draft(
    unique_id: str, generic_contact: Contact, generic_bank_account: BankAccount
):
    sale: Sale = shared_tests.draftable_order_object_tests(
        SaleDraft,
        "4000",
        unique_id,
        generic_contact,
        generic_bank_account,
    )

    assert sale is not None

    assert sale.settled is False

    sale.set_settled()

    assert sale.settled

    sale.delete("Test delete sale.")

    assert sale.deleted
