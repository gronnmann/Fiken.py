import datetime
from typing import Optional, List

from pydantic import BaseModel

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
)
from fiken_py.shared_types import Address, AccountingAccount, AccountingAccountAssets
from fiken_py.shared_enums import CompanyVatType


class Company(BaseModel, FikenObject):
    _GET_PATH_SINGLE = "/companies/{companySlug}"
    _GET_PATH_MULTIPLE = "/companies"

    name: Optional[str] = None
    slug: Optional[str] = None
    organizationNumber: Optional[str] = None
    vatType: Optional[CompanyVatType] = None
    address: Optional[Address] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    creationDate: Optional[str]
    hasApiAccess: Optional[bool] = None
    testCompany: Optional[bool] = None
    accountingStartDate: Optional[datetime.date] = None

    @property
    def id_attr(self):
        return "companySlug", self.slug

    # Inbox
    def get_inbox(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[InboxDocument]:
        return InboxDocument.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_inbox_document(self, documentId: int, **kwargs) -> InboxDocument | None:
        return InboxDocument.get(
            companySlug=self.slug,
            documentId=documentId,
            token=self._auth_token,
            **kwargs
        )

    def create_inbox_document_bytes(
        self, file: bytes, name: str, description: str, filename: str, **kwargs
    ) -> InboxDocument:
        return InboxDocument.upload_from_bytes(
            file=file,
            name=name,
            description=description,
            filename=filename,
            companySlug=self.slug,
            token=self._auth_token,
        )

    def create_inbox_document_filepath(
        self,
        filepath: str,
        name: str,
        description: str,
        filename: Optional[str] = None,
    ):
        return InboxDocument.upload_from_filepath(
            filepath=filepath,
            name=name,
            description=description,
            filename=filename,
            companySlug=self.slug,
            token=self._auth_token,
        )

    # Balance accounts

    def get_balance_accounts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[BalanceAccount]:
        return BalanceAccount.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_balance_account(
        self, accountCode: AccountingAccount | str, **kwargs
    ) -> BalanceAccount | None:
        if isinstance(accountCode, str):
            accountCode = AccountingAccount(accountCode)
        return BalanceAccount.get(
            companySlug=self.slug,
            accountCode=accountCode,
            token=self._auth_token,
            **kwargs
        )

    def get_balance_account_balances(
        self,
        date: datetime.date = datetime.date.today(),
        follow_pages: bool = True,
        page: Optional[int] = None,
        **kwargs
    ) -> List[BalanceAccountBalance]:
        return BalanceAccountBalance.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            date=date,
            token=self._auth_token,
            **kwargs
        )

    def get_balance_account_balance(
        self,
        accountCode: AccountingAccount | str,
        date: datetime.date = datetime.date.today(),
        **kwargs
    ) -> BalanceAccountBalance | None:
        if isinstance(accountCode, str):
            accountCode = AccountingAccount(accountCode)

        return BalanceAccountBalance.get(
            companySlug=self.slug,
            date=date,
            accountCode=accountCode,
            token=self._auth_token,
            **kwargs
        )

    # Bank accounts

    def get_bank_accounts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[BankAccount]:
        return BankAccount.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_bank_account(self, bankAccountId: int, **kwargs) -> BankAccount | None:
        return BankAccount.get(
            companySlug=self.slug,
            bankAccountId=bankAccountId,
            token=self._auth_token,
            **kwargs
        )

    def create_bank_account(self, bank_account: BankAccount, **kwargs) -> BankAccount:
        return bank_account.save(
            companySlug=self.slug, token=self._auth_token, **kwargs
        )

    # Contacts

    def get_contacts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Contact]:
        return Contact.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_contact(self, contactId: int, **kwargs) -> Contact | None:
        return Contact.get(
            companySlug=self.slug, contactId=contactId, token=self._auth_token, **kwargs
        )

    def create_contact(self, contact: Contact, **kwargs) -> Contact:
        if not contact.is_new:
            raise ValueError(
                "You cannot create a contact that already exists. Use save() to update it."
            )
        return contact.save(companySlug=self.slug, token=self._auth_token, **kwargs)

    # TODO - add groups

    # Product Sale Report

    def get_product_sale_report(
        self, from_date: datetime.date, to_date: datetime.date, **kwargs
    ) -> list[ProductSalesReport]:
        return ProductSalesReport.get_report_for_timeframe(
            from_date, to_date, token=self._auth_token, companySlug=self._company_slug, **kwargs
        )

    def get_products(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Product]:
        return Product.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_product(self, productId: int, **kwargs) -> Product | None:
        return Product.get(
            companySlug=self.slug, productId=productId, token=self._auth_token, **kwargs
        )

    def create_product(self, product: Product, **kwargs) -> Product:
        if not product.is_new:
            raise ValueError(
                "You cannot create a product that already exists. Use save() to update it."
            )
        return product.save(companySlug=self.slug, token=self._auth_token, **kwargs)

    # Journal Entries

    def get_journal_entries(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[JournalEntry]:
        return JournalEntry.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_journal_entry(self, journalEntryId: int, **kwargs) -> JournalEntry | None:
        return JournalEntry.get(
            companySlug=self.slug,
            journalEntryId=journalEntryId,
            token=self._auth_token,
            **kwargs
        )

    def create_transaction(
        self, transaction: Transaction, open: Optional[bool] = False, **kwargs
    ) -> Transaction:
        return transaction.save(
            companySlug=self.slug, token=self._auth_token, open=open, **kwargs
        )

    # Transactions

    def get_transactions(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Transaction]:
        return Transaction.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_transaction(self, transactionId: int, **kwargs) -> Transaction | None:
        return Transaction.get(
            companySlug=self.slug,
            transactionId=transactionId,
            token=self._auth_token,
            **kwargs
        )

    # Invoices

    def get_invoices(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Invoice]:
        return Invoice.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_invoice(self, invoiceId: int, **kwargs) -> Invoice | None:
        return Invoice.get(
            companySlug=self.slug, invoiceId=invoiceId, token=self._auth_token, **kwargs
        )

    def create_invoice(
        self,
        invoice: Invoice,
        bankAccountCode: AccountingAccountAssets | str,
        paymentAccount: Optional[AccountingAccount | str] = None,
        contactPersonId: Optional[int] = None,
        uuid: Optional[str] = None,
        **kwargs
    ) -> Invoice | None:
        return invoice.save(
            companySlug=self.slug,
            token=self._auth_token,
            bankAccountCode=bankAccountCode,
            uuid=uuid,
            paymentAccount=paymentAccount,
            contactPersonId=contactPersonId,
            **kwargs,
        )

    def get_invoice_drafts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[InvoiceDraft]:
        return InvoiceDraft.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_invoice_draft(self, draftId: int, **kwargs) -> InvoiceDraft | None:
        return InvoiceDraft.get(
            companySlug=self.slug, draftId=draftId, token=self._auth_token, **kwargs
        )

    def create_invoice_draft(
        self,
        invoice_draft: InvoiceDraft,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> InvoiceDraft:
        return invoice_draft.save(
            companySlug=self.slug,
            token=self._auth_token,
            contactId=contactId,
            contactPersonId=contactPersonId,
            **kwargs
        )

    # Credit Notes

    def get_credit_notes(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[CreditNote]:
        return CreditNote.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_credit_note(self, creditNoteId: int, **kwargs) -> CreditNote | None:
        return CreditNote.get(
            companySlug=self.slug,
            creditNoteId=creditNoteId,
            token=self._auth_token,
            **kwargs
        )

    def create_credit_note_from_invoice_full(
        self,
        invoiceId: int,
        creditNoteText: Optional[str] = None,
        issueDate=datetime.date.today(),
        **kwargs
    ) -> CreditNote:
        return CreditNote.create_from_invoice_full(
            invoiceId=invoiceId,
            issueDate=issueDate,
            creditNoteText=creditNoteText,
            companySlug=self.slug,
            token=self._auth_token,
            **kwargs
        )

    def get_credit_note_drafts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[CreditNoteDraft]:
        return CreditNoteDraft.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_credit_note_draft(self, draftId: int, **kwargs) -> CreditNoteDraft | None:
        return CreditNoteDraft.get(
            companySlug=self.slug, draftId=draftId, token=self._auth_token, **kwargs
        )

    def create_credit_note_draft(
        self,
        credit_note_draft: CreditNoteDraft,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> CreditNoteDraft:
        return credit_note_draft.save(
            companySlug=self.slug,
            token=self._auth_token,
            contactId=contactId,
            contactPersonId=contactPersonId,
            **kwargs
        )

    # Offers

    def get_offers(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Offer]:
        return Offer.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_offer(self, offerId: int, **kwargs) -> Offer | None:
        return Offer.get(
            companySlug=self.slug, offerId=offerId, token=self._auth_token, **kwargs
        )

    def get_offer_counter(self, **kwargs) -> int:
        return Offer.get_counter(
            companySlug=self.slug, token=self._auth_token, **kwargs
        )

    def set_initial_offer_counter(self, counter: int, **kwargs) -> int:
        return Offer.set_initial_counter(
            companySlug=self.slug, counter=counter, token=self._auth_token, **kwargs
        )

    def get_offer_drafts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[OfferDraft]:
        return OfferDraft.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_offer_draft(self, draftId: int, **kwargs) -> OfferDraft | None:
        return OfferDraft.get(
            companySlug=self.slug, draftId=draftId, token=self._auth_token, **kwargs
        )

    def create_offer_draft(
        self,
        offer_draft: OfferDraft,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> OfferDraft:
        return offer_draft.save(
            companySlug=self.slug,
            token=self._auth_token,
            contactId=contactId,
            contactPersonId=contactPersonId,
            **kwargs
        )

    # Order confirmations

    def get_order_confirmations(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> (List)[OrderConfirmation]:
        return OrderConfirmation.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_order_confirmation(
        self, orderConfirmationId: int, **kwargs
    ) -> OrderConfirmation | None:
        return OrderConfirmation.get(
            companySlug=self.slug,
            orderConfirmationId=orderConfirmationId,
            token=self._auth_token,
            **kwargs
        )

    def get_order_confirmation_counter(self, **kwargs) -> int:
        return OrderConfirmation.get_counter(
            companySlug=self.slug, token=self._auth_token, **kwargs
        )

    def set_initial_order_confirmation_counter(self, counter: int, **kwargs) -> int:
        return OrderConfirmation.set_initial_counter(
            companySlug=self.slug, counter=counter, token=self._auth_token, **kwargs
        )

    def get_order_confirmation_drafts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> (List)[OrderConfirmationDraft]:
        return OrderConfirmationDraft.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_order_confirmation_draft(
        self, draftId: int, **kwargs
    ) -> OrderConfirmationDraft | None:
        return OrderConfirmationDraft.get(
            companySlug=self.slug, draftId=draftId, token=self._auth_token, **kwargs
        )

    def create_order_confirmation_draft(
        self, order_confirmation_draft: OrderConfirmationDraft, **kwargs
    ) -> OrderConfirmationDraft:
        return order_confirmation_draft.save(
            companySlug=self.slug, token=self._auth_token, **kwargs
        )

    # Sales

    def get_sales(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Sale]:
        return Sale.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_sale(self, saleId: int, **kwargs) -> Sale | None:
        return Sale.get(
            companySlug=self.slug, saleId=saleId, token=self._auth_token, **kwargs
        )

    def create_sale(
        self, sale: Sale, paymentFee: Optional[int] = None, **kwargs
    ) -> Sale:
        return sale.save(
            companySlug=self.slug,
            token=self._auth_token,
            paymentFee=paymentFee,
            **kwargs
        )

    def get_sale_drafts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[SaleDraft]:
        return SaleDraft.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_sale_draft(self, draftId: int, **kwargs) -> SaleDraft | None:
        return SaleDraft.get(
            companySlug=self.slug, draftId=draftId, token=self._auth_token, **kwargs
        )

    def create_sale_draft(self, sale_draft: SaleDraft, **kwargs) -> SaleDraft:
        return sale_draft.save(companySlug=self.slug, token=self._auth_token, **kwargs)

    # Purchases

    def get_purchases(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Purchase]:
        return Purchase.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_purchase(self, purchaseId: int, **kwargs) -> Purchase | None:
        return Purchase.get(
            companySlug=self.slug,
            purchaseId=purchaseId,
            token=self._auth_token,
            **kwargs
        )

    def create_purchase(
        self, purchase: Purchase, projectId: Optional[int] = None, **kwargs
    ) -> Purchase:
        return purchase.save(
            companySlug=self.slug, token=self._auth_token, projectId=projectId, **kwargs
        )

    def get_purchase_drafts(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[PurchaseDraft]:
        return PurchaseDraft.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_purchase_draft(self, draftId: int, **kwargs) -> PurchaseDraft | None:
        return PurchaseDraft.get(
            companySlug=self.slug, draftId=draftId, token=self._auth_token, **kwargs
        )

    def create_purchase_draft(
        self, purchase_draft: PurchaseDraft, **kwargs
    ) -> PurchaseDraft:
        return purchase_draft.save(
            companySlug=self.slug, token=self._auth_token, **kwargs
        )

    # Projects

    def get_projects(
        self, follow_pages: bool = True, page: Optional[int] = None, **kwargs
    ) -> List[Project]:
        return Project.getAll(
            companySlug=self.slug,
            follow_pages=follow_pages,
            page=page,
            token=self._auth_token,
            **kwargs
        )

    def get_project(self, projectId: int, **kwargs) -> Project | None:
        return Project.get(
            companySlug=self.slug, projectId=projectId, token=self._auth_token, **kwargs
        )

    def create_project(self, project: Project, **kwargs) -> Project:
        return project.save(companySlug=self.slug, token=self._auth_token, **kwargs)
