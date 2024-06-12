from fiken_py.models import InboxDocumentRequest, InboxDocument


def test_inbox_documents(unique_id):
    with open("test_online/dummy_attachment.pdf", "rb") as f:
        file_bytes = f.read()

    inbox_document_bytes = InboxDocumentRequest(
        name=f"Testdokument {unique_id}",
        filename="dummy_doc.pdf",
        file=file_bytes,
        description="Dette er en test ved bytes opplasting",
    )

    inbox_document = InboxDocumentRequest.from_filepath(
        name=f"Testdokument {unique_id}",
        filepath="test_online/dummy_attachment.pdf",
        description="Dette er en test ved filepath opplasting",
    )

    inbox_document_bytes = inbox_document_bytes.save()
    inbox_document = inbox_document.save()

    inbox_documents = InboxDocument.getAll()
    assert inbox_documents is not None
    assert len(inbox_documents) > 0

    assert InboxDocument.get(inboxDocumentId=inbox_document.documentId) is not None
    assert (
        InboxDocument.get(inboxDocumentId=inbox_document_bytes.documentId) is not None
    )
