import hashlib
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from aletheia.core.storage import StorageError, get_storage
from aletheia.main import app
from aletheia.modules.cases.models import Case, CaseStatus
from aletheia.modules.evidence.models import Evidence, EvidenceStatus
from aletheia.modules.organizations.models import Membership, MembershipRole
from tests import samples
from tests.factories import Account

pytestmark = pytest.mark.integration

AccountFactory = Callable[[], Account]


@pytest.fixture
def firm(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> Iterator[dict[str, Any]]:
    """A lead lawyer with one active case, plus a colleague in the same organization."""
    lead, colleague = make_account(), make_account()
    db_session.add(
        Membership(
            organization_id=lead.organization_id,
            user_id=colleague.user_id,
            role=MembershipRole.LAWYER,
        )
    )
    db_session.commit()
    case = api_client.post(
        f"/api/v1/organizations/{lead.organization_id}/cases",
        json={"title": "Proceso de alimentos"},
        headers=lead.headers,
    ).json()
    case_url = f"/api/v1/organizations/{lead.organization_id}/cases/{case['id']}"
    yield {
        "lead": lead,
        "colleague": colleague,
        "case_id": uuid.UUID(case["id"]),
        "case_url": case_url,
        "evidence_url": f"{case_url}/evidence",
    }
    # Originals are never deleted by the application; tests remove their own objects.
    storage = get_storage()
    prefix = f"organizations/{lead.organization_id}/"
    listing = storage._client.list_objects_v2(Bucket=storage._bucket, Prefix=prefix)
    for item in listing.get("Contents", []):
        if key := item.get("Key"):
            storage._client.delete_object(Bucket=storage._bucket, Key=key)


def upload(
    client: TestClient,
    url: str,
    account: Account,
    content: bytes = samples.PDF,
    filename: str = "contrato.pdf",
) -> Any:
    return client.post(url, files={"file": (filename, content)}, headers=account.headers)


# --- preservation ------------------------------------------------------------


def test_upload_preserves_the_file_with_its_sha256(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    response = upload(api_client, firm["evidence_url"], firm["lead"])

    assert response.status_code == 201
    body = response.json()
    assert body["reference"] == f"EVD-{datetime.now(UTC).year}-000001"
    assert body["sha256"] == hashlib.sha256(samples.PDF).hexdigest()
    assert body["media_type"] == "application/pdf"
    assert body["size_bytes"] == len(samples.PDF)
    assert body["status"] == "preserved"
    assert body["preserved_at"] is not None


def test_stored_original_is_byte_for_byte_identical(
    api_client: TestClient, db_session: Session, firm: dict[str, Any]
) -> None:
    body = upload(api_client, firm["evidence_url"], firm["lead"]).json()

    evidence = db_session.get(Evidence, uuid.UUID(body["id"]))
    assert evidence is not None
    stored = get_storage().read_object(evidence.storage_key)
    assert stored == samples.PDF
    assert hashlib.sha256(stored).hexdigest() == evidence.sha256


def test_storage_key_never_contains_the_user_filename(
    api_client: TestClient, db_session: Session, firm: dict[str, Any]
) -> None:
    body = upload(
        api_client, firm["evidence_url"], firm["lead"], filename="../../secreto.pdf"
    ).json()

    evidence = db_session.get(Evidence, uuid.UUID(body["id"]))
    assert evidence is not None
    assert body["original_filename"] == "secreto.pdf"
    assert "secreto" not in evidence.storage_key
    assert evidence.storage_key.endswith(f"/evidence/{evidence.id}/original")


def test_evidence_can_be_listed_and_read(api_client: TestClient, firm: dict[str, Any]) -> None:
    created = upload(api_client, firm["evidence_url"], firm["lead"]).json()

    listed = api_client.get(firm["evidence_url"], headers=firm["lead"].headers)
    detail = api_client.get(f"{firm['evidence_url']}/{created['id']}", headers=firm["lead"].headers)

    assert [item["id"] for item in listed.json()] == [created["id"]]
    assert detail.status_code == 200
    assert detail.json()["uploaded_by"] == str(firm["lead"].user_id)


# --- rejections --------------------------------------------------------------


def test_identical_content_cannot_be_preserved_twice_in_a_case(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    upload(api_client, firm["evidence_url"], firm["lead"])

    response = upload(api_client, firm["evidence_url"], firm["lead"], filename="copia.pdf")

    assert response.status_code == 409
    assert response.json()["code"] == "EVIDENCE_ALREADY_EXISTS"


@pytest.mark.parametrize(
    ("filename", "content", "status_code", "code"),
    [
        ("programa.exe", samples.WINDOWS_EXECUTABLE, 415, "UNSUPPORTED_FILE_TYPE"),
        ("factura.pdf", samples.WINDOWS_EXECUTABLE, 415, "FILE_TYPE_MISMATCH"),
        ("vacio.pdf", b"", 422, "EMPTY_FILE"),
    ],
)
def test_unacceptable_files_are_rejected_without_a_record(
    api_client: TestClient,
    firm: dict[str, Any],
    filename: str,
    content: bytes,
    status_code: int,
    code: str,
) -> None:
    response = upload(api_client, firm["evidence_url"], firm["lead"], content, filename)

    assert response.status_code == status_code
    assert response.json()["code"] == code
    assert api_client.get(firm["evidence_url"], headers=firm["lead"].headers).json() == []


def test_evidence_cannot_be_added_to_an_inactive_case(
    api_client: TestClient, db_session: Session, firm: dict[str, Any]
) -> None:
    case = db_session.get(Case, firm["case_id"])
    assert case is not None
    case.status = CaseStatus.CLOSED
    db_session.commit()

    response = upload(api_client, firm["evidence_url"], firm["lead"])

    assert response.status_code == 409
    assert response.json()["code"] == "CASE_NOT_ACTIVE"


# --- access control ----------------------------------------------------------


def test_viewers_can_read_but_not_upload(api_client: TestClient, firm: dict[str, Any]) -> None:
    colleague = firm["colleague"]
    api_client.post(
        f"{firm['case_url']}/members",
        json={"user_id": str(colleague.user_id), "role": "viewer"},
        headers=firm["lead"].headers,
    )

    listed = api_client.get(firm["evidence_url"], headers=colleague.headers)
    uploaded = upload(api_client, firm["evidence_url"], colleague)

    assert listed.status_code == 200
    assert uploaded.status_code == 403
    assert uploaded.json()["code"] == "PERMISSION_DENIED"


def test_organization_members_outside_the_case_cannot_see_its_evidence(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    upload(api_client, firm["evidence_url"], firm["lead"])

    response = api_client.get(firm["evidence_url"], headers=firm["colleague"].headers)

    assert response.status_code == 404
    assert response.json()["code"] == "CASE_NOT_FOUND"


def test_evidence_of_another_case_is_not_reachable(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    created = upload(api_client, firm["evidence_url"], firm["lead"]).json()
    other_case = api_client.post(
        f"/api/v1/organizations/{firm['lead'].organization_id}/cases",
        json={"title": "Otro caso"},
        headers=firm["lead"].headers,
    ).json()
    other_url = (
        f"/api/v1/organizations/{firm['lead'].organization_id}/cases/{other_case['id']}/evidence"
    )

    response = api_client.get(f"{other_url}/{created['id']}", headers=firm["lead"].headers)

    assert response.status_code == 404
    assert response.json()["code"] == "EVIDENCE_NOT_FOUND"


# --- storage failures --------------------------------------------------------


class FailingUploadStorage:
    def put_new_object(self, *args: object, **kwargs: object) -> None:
        raise StorageError("storage unavailable")


def test_failed_upload_is_recorded_as_failed_and_can_be_retried(
    api_client: TestClient, db_session: Session, firm: dict[str, Any]
) -> None:
    app.dependency_overrides[get_storage] = FailingUploadStorage
    failed = upload(api_client, firm["evidence_url"], firm["lead"])
    del app.dependency_overrides[get_storage]

    retried = upload(api_client, firm["evidence_url"], firm["lead"])

    assert failed.status_code == 503
    assert failed.json()["code"] == "EVIDENCE_STORAGE_UNAVAILABLE"
    assert retried.status_code == 201
    statuses = sorted(
        item["status"]
        for item in api_client.get(firm["evidence_url"], headers=firm["lead"].headers).json()
    )
    assert statuses == [EvidenceStatus.FAILED.value, EvidenceStatus.PRESERVED.value]
