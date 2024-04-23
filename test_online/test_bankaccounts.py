from fiken_py.fiken_types import BankAccountType
from fiken_py.models import BankAccount, BankAccountCreateRequest


def test_create_bankaccount(unique_id):
    bank_account_request: BankAccountCreateRequest = BankAccountCreateRequest(
        name=f"Test account ({unique_id})",
        bankAccountNumber="11112233334",
        type=BankAccountType.NORMAL,
    )

    bank_account: BankAccount = bank_account_request.save()

    assert bank_account.bankAccountId is not None
    assert bank_account.name == bank_account_request.name
    assert bank_account.bankAccountNumber == bank_account_request.bankAccountNumber


def test_get_accounts():
    bank_accounts = BankAccount.getAll()

    assert bank_accounts is not None
    assert len(bank_accounts) > 0


def test_get_account(unique_id):
    bank_accounts = BankAccount.getAll()

    found = False
    for account in bank_accounts:
        if account.name == f"Test account ({unique_id})":
            found = True
            break

    assert found

    acc_id = account.bankAccountId

    bank_account = BankAccount.get(bankAccountId=acc_id)