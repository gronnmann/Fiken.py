import datetime

from fiken_py.models import BalanceAccount, SaleRequest
from fiken_py.shared_enums import SaleKind
from fiken_py.shared_types import OrderLine


def test_with_sale(unique_id, generic_product, generic_bank_account):
    acc_sales: BalanceAccount = BalanceAccount.get(accountCode="3000")

    assert acc_sales is not None

    old_balance = acc_sales.get_balance()

    assert old_balance is not None

    sale = SaleRequest(
        date=datetime.date.today(),
        paymentDate=datetime.date.today(),
        paymentAccount=generic_bank_account.accountCode,
        kind=SaleKind.CASH_SALE,
        lines=[
            OrderLine(
                account="3000",
                netPrice=100,
                vat=25,
                vatType="HIGH",
                description=f"Test sale - test_balance_accounts ({unique_id})",
            )
        ],
        totalPaid=125,
        currency="NOK",
    )

    sale: SaleRequest = sale.save()

    new_balance = acc_sales.get_balance()

    diff = new_balance.balance - old_balance.balance

    assert diff == -100