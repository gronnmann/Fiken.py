from fiken_py.models import BankAccount, Transaction, JournalEntry
from test_online import sample_object_factory, shared_tests


def test_journal_entry(unique_id, generic_bank_account):
    ba_2 = sample_object_factory.bank_account_request(unique_id)
    ba_2: BankAccount = ba_2.save()

    je_req = sample_object_factory.journal_entry_request(
        unique_id, generic_bank_account, ba_2
    )

    t: Transaction = je_req.save()

    assert len(t.entries) == 1

    j: JournalEntry = JournalEntry.get(journalEntryId=t.entries[0].journalEntryId)
    assert j.journalEntryId is not None

    shared_tests.attachable_object_tests(j, False)
