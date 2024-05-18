import datetime

from fiken_py.models import PurchaseRequest, Purchase
from fiken_py.shared_enums import PurchaseKind
from fiken_py.shared_types import OrderLine, Payment


def test_purchase_all(unique_id: str, generic_bank_account):
    purchase_line = OrderLine(
        description=f"En veldig stor hagesaks (testprodukt {unique_id})",
        vatType="HIGH",
        account="4300",
        netPrice=1000,
    )

    purchase_request = PurchaseRequest(
        date=datetime.date.today(),
        kind=PurchaseKind.CASH_PURCHASE,
        currency="NOK",
        lines=[purchase_line],
        paid=True,
        paymentAccount=generic_bank_account.bankAccountNumber,
        paymentDate=datetime.date.today(),
    )

    purchase: Purchase = purchase_request.save()


    assert purchase is not None
    assert purchase.purchaseId is not None
    assert purchase.deleted is False

    assert len(purchase.payments) == 0

    payment = Payment(
        date=datetime.date.today(),
        amount=500,
        account=generic_bank_account.bankAccountNumber,
    )
    payment: Payment = purchase.create_payment(payment)

    assert len(purchase.payments) == 1
    assert purchase.payments[0].amount == 500

    assert purchase.get_payment(payment.paymentId) is not None

    set_deleted = purchase.delete()

    assert set_deleted.deleted is True
