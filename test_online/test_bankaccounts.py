from fiken_py.models import BankAccount, BankAccountRequest, BankAccountType


def test_create_bankaccount(unique_id):
    bank_account_request: BankAccountRequest = BankAccountRequest(
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
    acc_name = f"Test account ({unique_id})"
    print(f"Searching for account with name {acc_name}")

    bank_accounts = BankAccount.getAll()

    found = False
    for account in bank_accounts:
        if account.name == acc_name:
            found = True
            break

    assert found

    acc_id = account.bankAccountId

    bank_account = BankAccount.get(bankAccountId=acc_id)


def test_random_account_not_found():
    random_id = 21112233334

    while True:
        print(f"Trying to find with {random_id}")
        acc = BankAccount.get(bankAccountId=str(random_id))
        if acc is None:
            break
        random_id += 1

    get_single_acc = BankAccount.get(bankAccountId=str(random_id))
    assert get_single_acc is None
