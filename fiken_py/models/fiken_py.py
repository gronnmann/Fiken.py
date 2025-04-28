import datetime
from typing import List, Optional

from fiken_py.fikenoauth import AccessToken
from fiken_py.fiken_object import FikenObject
from fiken_py.models import (
    BalanceAccount, 
    BankAccount, 
    Contact, 
    ProductSalesReport, 
    Product, 
    JournalEntry, 
    Transaction, 
    InboxDocument, 
    Invoice, 
    InvoiceDraft, 
    CreditNote, 
    CreditNoteDraft, 
    Offer, 
    OfferDraft, 
    OrderConfirmation, 
    OrderConfirmationDraft, 
    Sale, 
    SaleDraft, 
    Purchase, 
    PurchaseDraft, 
    Project, 
    BalanceAccountBalance, 
    UserInfo, 
    Company
)
from fiken_py.shared_types import Address, AccountingAccount, AccountingAccountAssets
from fiken_py.shared_enums import CompanyVatType


class FikenPy:
    """Class for interacting with the Fiken API using an OOP approach.
    Create this class after obtaining an access token, and then use its methods to interact with the API.
    """

    def __init__(self, auth_token: str | AccessToken):
        if FikenObject._AUTH_TOKEN is not None:
            raise ValueError(
                "Global auth token already set (FikenObject.set_auth_token). "
                "Please clear it before setting individual tokens."
            )

        self.access_token = auth_token

    def get_user_info(self) -> UserInfo | None:
        return UserInfo.get(token=self.access_token)

    def get_companies(self) -> List[Company]:
        return Company.getAll(token=self.access_token)

    def get_company(self, company_slug: str) -> Company | None:
        return Company.get(companySlug=company_slug, token=self.access_token)
        
    # Inbox
    def get_inbox(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[InboxDocument]:
        return InboxDocument.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_inbox_document(self, company_slug: str, documentId: int, **kwargs) -> InboxDocument | None:
        return InboxDocument.get(
            companySlug=company_slug,
            documentId=documentId,
            token=self.access_token,
            **kwargs
        )

    def create_inbox_document_bytes(
        self, company_slug: str, file: bytes, name: str, description: str, filename: str, **kwargs
    ) -> InboxDocument:
        return InboxDocument.upload_from_bytes(
            file=file,
            name=name,
            description=description,
            filename=filename,
            companySlug=company_slug,
            token=self.access_token,
        )

    def create_inbox_document_filepath(
        self,
        company_slug: str,
        filepath: str,
        name: str,
        description: str,
        filename: Optional[str] = None,
        **kwargs
    ):
        return InboxDocument.upload_from_filepath(
            filepath=filepath,
            name=name,
            description=description,
            filename=filename,
            companySlug=company_slug,
            token=self.access_token,
            **kwargs
        )

    # Balance accounts

    def get_balance_accounts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[BalanceAccount]:
        return BalanceAccount.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_balance_account(
        self, company_slug: str, accountCode: AccountingAccount | str, **kwargs
    ) -> BalanceAccount | None:
        if isinstance(accountCode, str):
            accountCode = AccountingAccount(accountCode)
        return BalanceAccount.get(
            companySlug=company_slug,
            accountCode=accountCode,
            token=self.access_token,
            **kwargs
        )

    def get_balance_account_balances(
        self,
        company_slug: str,
        date: datetime.date = datetime.date.today(),
        follow_pages: bool = True,
        page: Optional[int] = None,
        **kwargs
    ) -> List[BalanceAccountBalance]:
        return BalanceAccountBalance.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            date=date,
            token=self.access_token,
            **kwargs
        )

    def get_balance_account_balance(
        self,
        company_slug: str,
        accountCode: AccountingAccount | str,
        date: datetime.date = datetime.date.today(),
        **kwargs
    ) -> BalanceAccountBalance | None:
        if isinstance(accountCode, str):
            accountCode = AccountingAccount(accountCode)

        return BalanceAccountBalance.get(
            companySlug=company_slug,
            date=date,
            accountCode=accountCode,
            token=self.access_token,
            **kwargs
        )

    # Bank accounts

    def get_bank_accounts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[BankAccount]:
        return BankAccount.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_bank_account(self, company_slug: str, bankAccountId: int, **kwargs) -> BankAccount | None:
        return BankAccount.get(
            companySlug=company_slug,
            bankAccountId=bankAccountId,
            token=self.access_token,
            **kwargs
        )

    def create_bank_account(self, company_slug: str, bank_account: BankAccount, **kwargs) -> BankAccount:
        return bank_account.save(
            companySlug=company_slug, token=self.access_token, **kwargs
        )

    # Contacts

    def get_contacts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Contact]:
        return Contact.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_contact(self, company_slug: str, contactId: int, **kwargs) -> Contact | None:
        return Contact.get(
            companySlug=company_slug, contactId=contactId, token=self.access_token, **kwargs
        )

    def create_contact(self, company_slug: str, contact: Contact, **kwargs) -> Contact:
        if not contact.is_new:
            raise ValueError(
                "You cannot create a contact that already exists. Use save() to update it."
            )
        return contact.save(companySlug=company_slug, token=self.access_token, **kwargs)

    # Product Sale Report

    def get_product_sale_report(
        self, company_slug: str, from_date: datetime.date, to_date: datetime.date, **kwargs
    ) -> list[ProductSalesReport]:
        return ProductSalesReport.get_report_for_timeframe(
            from_date, to_date, token=self.access_token, companySlug=company_slug, **kwargs
        )

    def get_products(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Product]:
        return Product.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_product(self, company_slug: str, productId: int, **kwargs) -> Product | None:
        return Product.get(
            companySlug=company_slug, productId=productId, token=self.access_token, **kwargs
        )

    def create_product(self, company_slug: str, product: Product, **kwargs) -> Product:
        if not product.is_new:
            raise ValueError(
                "You cannot create a product that already exists. Use save() to update it."
            )
        return product.save(companySlug=company_slug, token=self.access_token, **kwargs)

    # Journal Entries

    def get_journal_entries(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[JournalEntry]:
        return JournalEntry.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_journal_entry(self, company_slug: str, journalEntryId: int, **kwargs) -> JournalEntry | None:
        return JournalEntry.get(
            companySlug=company_slug,
            journalEntryId=journalEntryId,
            token=self.access_token,
            **kwargs
        )

    def create_transaction(
        self, company_slug: str, transaction: Transaction, open: Optional[bool] = False, **kwargs
    ) -> Transaction:
        return transaction.save(
            companySlug=company_slug, token=self.access_token, open=open, **kwargs
        )

    # Transactions

    def get_transactions(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Transaction]:
        return Transaction.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_transaction(self, company_slug: str, transactionId: int, **kwargs) -> Transaction | None:
        return Transaction.get(
            companySlug=company_slug,
            transactionId=transactionId,
            token=self.access_token,
            **kwargs
        )

    # Invoices

    def get_invoices(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Invoice]:
        return Invoice.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_invoice(self, company_slug: str, invoiceId: int, **kwargs) -> Invoice | None:
        return Invoice.get(
            companySlug=company_slug, invoiceId=invoiceId, token=self.access_token, **kwargs
        )

    def create_invoice(
        self,
        company_slug: str,
        invoice: Invoice,
        bankAccountCode: AccountingAccountAssets | str,
        paymentAccount: Optional[AccountingAccount | str] = None,
        contactPersonId: Optional[int] = None,
        uuid: Optional[str] = None,
        **kwargs
    ) -> Invoice | None:
        return invoice.save(
            companySlug=company_slug,
            token=self.access_token,
            bankAccountCode=bankAccountCode,
            uuid=uuid,
            paymentAccount=paymentAccount,
            contactPersonId=contactPersonId,
            **kwargs,
        )

    def get_invoice_drafts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[InvoiceDraft]:
        return InvoiceDraft.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_invoice_draft(self, company_slug: str, draftId: int, **kwargs) -> InvoiceDraft | None:
        return InvoiceDraft.get(
            companySlug=company_slug, draftId=draftId, token=self.access_token, **kwargs
        )

    def create_invoice_draft(
        self,
        company_slug: str,
        invoice_draft: InvoiceDraft,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> InvoiceDraft:
        return invoice_draft.save(
            companySlug=company_slug,
            token=self.access_token,
            contactId=contactId,
            contactPersonId=contactPersonId,
            **kwargs
        )

    # Credit Notes

    def get_credit_notes(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[CreditNote]:
        return CreditNote.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_credit_note(self, company_slug: str, creditNoteId: int, **kwargs) -> CreditNote | None:
        return CreditNote.get(
            companySlug=company_slug,
            creditNoteId=creditNoteId,
            token=self.access_token,
            **kwargs
        )

    def create_credit_note_from_invoice_full(
        self,
        company_slug: str,
        invoiceId: int,
        creditNoteText: Optional[str] = None,
        issueDate=datetime.date.today(),
        **kwargs
    ) -> CreditNote:
        return CreditNote.create_from_invoice_full(
            invoiceId=invoiceId,
            issueDate=issueDate,
            creditNoteText=creditNoteText,
            companySlug=company_slug,
            token=self.access_token,
            **kwargs
        )

    def get_credit_note_drafts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[CreditNoteDraft]:
        return CreditNoteDraft.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_credit_note_draft(self, company_slug: str, draftId: int, **kwargs) -> CreditNoteDraft | None:
        return CreditNoteDraft.get(
            companySlug=company_slug, draftId=draftId, token=self.access_token, **kwargs
        )

    def create_credit_note_draft(
        self,
        company_slug: str,
        credit_note_draft: CreditNoteDraft,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> CreditNoteDraft:
        return credit_note_draft.save(
            companySlug=company_slug,
            token=self.access_token,
            contactId=contactId,
            contactPersonId=contactPersonId,
            **kwargs
        )

    # Offers

    def get_offers(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Offer]:
        return Offer.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_offer(self, company_slug: str, offerId: int, **kwargs) -> Offer | None:
        return Offer.get(
            companySlug=company_slug, offerId=offerId, token=self.access_token, **kwargs
        )

    def get_offer_counter(self, company_slug: str, **kwargs) -> int:
        return Offer.get_counter(
            companySlug=company_slug, token=self.access_token, **kwargs
        )

    def set_initial_offer_counter(self, company_slug: str, counter: int, **kwargs) -> int:
        return Offer.set_initial_counter(
            companySlug=company_slug, counter=counter, token=self.access_token, **kwargs
        )

    def get_offer_drafts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[OfferDraft]:
        return OfferDraft.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_offer_draft(self, company_slug: str, draftId: int, **kwargs) -> OfferDraft | None:
        return OfferDraft.get(
            companySlug=company_slug, draftId=draftId, token=self.access_token, **kwargs
        )

    def create_offer_draft(
        self,
        company_slug: str,
        offer_draft: OfferDraft,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> OfferDraft:
        return offer_draft.save(
            companySlug=company_slug,
            token=self.access_token,
            contactId=contactId,
            contactPersonId=contactPersonId,
            **kwargs
        )

    # Order confirmations

    def get_order_confirmations(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[OrderConfirmation]:
        return OrderConfirmation.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_order_confirmation(
        self, company_slug: str, orderConfirmationId: int, **kwargs
    ) -> OrderConfirmation | None:
        return OrderConfirmation.get(
            companySlug=company_slug,
            orderConfirmationId=orderConfirmationId,
            token=self.access_token,
            **kwargs
        )

    def get_order_confirmation_counter(self, company_slug: str, **kwargs) -> int:
        return OrderConfirmation.get_counter(
            companySlug=company_slug, token=self.access_token, **kwargs
        )

    def set_initial_order_confirmation_counter(self, company_slug: str, counter: int, **kwargs) -> int:
        return OrderConfirmation.set_initial_counter(
            companySlug=company_slug, counter=counter, token=self.access_token, **kwargs
        )

    def get_order_confirmation_drafts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[OrderConfirmationDraft]:
        return OrderConfirmationDraft.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_order_confirmation_draft(
        self, company_slug: str, draftId: int, **kwargs
    ) -> OrderConfirmationDraft | None:
        return OrderConfirmationDraft.get(
            companySlug=company_slug, draftId=draftId, token=self.access_token, **kwargs
        )

    def create_order_confirmation_draft(
        self, company_slug: str, order_confirmation_draft: OrderConfirmationDraft, **kwargs
    ) -> OrderConfirmationDraft:
        return order_confirmation_draft.save(
            companySlug=company_slug, token=self.access_token, **kwargs
        )

    # Sales

    def get_sales(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Sale]:
        return Sale.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_sale(self, company_slug: str, saleId: int, **kwargs) -> Sale | None:
        return Sale.get(
            companySlug=company_slug, saleId=saleId, token=self.access_token, **kwargs
        )

    def create_sale(
        self, company_slug: str, sale: Sale, paymentFee: Optional[int] = None, **kwargs
    ) -> Sale:
        return sale.save(
            companySlug=company_slug,
            token=self.access_token,
            paymentFee=paymentFee,
            **kwargs
        )

    def get_sale_drafts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[SaleDraft]:
        return SaleDraft.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_sale_draft(self, company_slug: str, draftId: int, **kwargs) -> SaleDraft | None:
        return SaleDraft.get(
            companySlug=company_slug, draftId=draftId, token=self.access_token, **kwargs
        )

    def create_sale_draft(self, company_slug: str, sale_draft: SaleDraft, **kwargs) -> SaleDraft:
        return sale_draft.save(companySlug=company_slug, token=self.access_token, **kwargs)

    # Purchases

    def get_purchases(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Purchase]:
        return Purchase.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_purchase(self, company_slug: str, purchaseId: int, **kwargs) -> Purchase | None:
        return Purchase.get(
            companySlug=company_slug,
            purchaseId=purchaseId,
            token=self.access_token,
            **kwargs
        )

    def create_purchase(
        self, company_slug: str, purchase: Purchase, projectId: Optional[int] = None, **kwargs
    ) -> Purchase:
        return purchase.save(
            companySlug=company_slug, token=self.access_token, projectId=projectId, **kwargs
        )

    def get_purchase_drafts(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[PurchaseDraft]:
        return PurchaseDraft.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_purchase_draft(self, company_slug: str, draftId: int, **kwargs) -> PurchaseDraft | None:
        return PurchaseDraft.get(
            companySlug=company_slug, draftId=draftId, token=self.access_token, **kwargs
        )

    def create_purchase_draft(
        self, company_slug: str, purchase_draft: PurchaseDraft, **kwargs
    ) -> PurchaseDraft:
        return purchase_draft.save(
            companySlug=company_slug, token=self.access_token, **kwargs
        )

    # Projects

    def get_projects(
        self, company_slug: str, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Project]:
        return Project.getAll(
            companySlug=company_slug,
            follow_pages=follow_pages,
            page=page,
            token=self.access_token,
            **kwargs
        )

    def get_project(self, company_slug: str, projectId: int, **kwargs) -> Project | None:
        return Project.get(
            companySlug=company_slug, projectId=projectId, token=self.access_token, **kwargs
        )

    def create_project(self, company_slug: str, project: Project, **kwargs) -> Project:
        return project.save(companySlug=company_slug, token=self.access_token, **kwargs)
