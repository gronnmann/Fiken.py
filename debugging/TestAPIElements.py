import os

import dotenv

from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Company, BankAccount
from fiken_py.fiken_types import BankAccountType

dotenv.load_dotenv(".env")

FikenObject.set_auth_token(os.getenv("FIKEN_API_TOKEN"))

def get_user_info():
    user = UserInfo.get()
    print(user)


def get_companies():
    companies = Company.getAll(sortBy='name desc')

    for company in companies:
        print(company)

def get_company():
    company = Company.get(companySlug='fiken-demo-drage-og-elefant-as')
    print(company)

def get_bank_accounts():
    # bank_accounts = BankAccount.getAll(companySlug='fiken-demo-drage-og-elefant-as')

    demo_konto = BankAccount.get(companySlug='fiken-demo-drage-og-elefant-as', bankAccountId=2882125076)
    print(demo_konto)

def create_bank_account():
    new_account = BankAccount(name="Testkonto", bankAccountNumber="11152233334 "
                              , type=BankAccountType.NORMAL)
    new_account.save(companySlug='fiken-demo-drage-og-elefant-as')

    print("New account created")
    print(new_account)


if __name__ == "__main__":
    # get_bank_accounts()
    create_bank_account()