import base64
import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import boto3
import pytest
from crossword_solver_domain_entities.image_file import ImageFile
from moto import mock_aws

from crossword_solver_adapter_storage.s3_image_store import S3ImageStore, import_id_from_upload_key

BUCKET = "puzzle-images"
URL_PREFIX = f"s3://{BUCKET}/images/"


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3", region_name="eu-west-2")
        client.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        yield client


@pytest.fixture
def store(s3) -> S3ImageStore:
    return S3ImageStore(BUCKET, client=s3)


def test_save_puts_the_content_in_the_bucket_and_returns_its_s3_url(store, s3):
    url = store.save(ImageFile("puzzle14.jpg", b"image-bytes"))

    assert url.startswith(URL_PREFIX)
    assert url.endswith("/puzzle14.jpg")
    stored = s3.get_object(Bucket=BUCKET, Key=url.removeprefix(f"s3://{BUCKET}/"))
    assert stored["Body"].read() == b"image-bytes"
    assert stored["ContentType"] == "image/jpeg"


def test_save_puts_files_with_the_same_name_in_different_locations(store):
    first = store.save(ImageFile("puzzle14.jpg", b"first"))
    second = store.save(ImageFile("puzzle14.jpg", b"second"))

    assert first != second


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("../../etc/passwd.png", "passwd.png"),
        ("C:\\Users\\me\\puzzle 14 (1).jpg", "puzzle_14__1_.jpg"),
        ("pu\nzzle\r.jpg", "pu_zzle_.jpg"),
        ("..", "image"),
        ("", "image"),
        ("a" * 150 + ".png", "a" * 96 + ".png"),
    ],
    ids=["path traversal", "windows path", "control characters", "dots only", "empty", "long"],
)
def test_save_makes_the_filename_safe_for_the_key(store, filename, expected):
    url = store.save(ImageFile(filename, b"image-bytes"))

    assert url.rsplit("/", 1)[1] == expected


def test_save_uses_a_default_content_type_for_unknown_extensions(store, s3):
    url = store.save(ImageFile("puzzle", b"image-bytes"))

    stored = s3.get_object(Bucket=BUCKET, Key=url.removeprefix(f"s3://{BUCKET}/"))
    assert stored["ContentType"] == "application/octet-stream"


def test_create_upload_returns_a_form_for_the_import_and_where_it_will_be_stored(store):
    import_id = uuid4()

    upload = store.create_upload(import_id, "../puzzle 14.png", 1024)

    key = f"uploads/{import_id}/puzzle_14.png"
    assert upload.image_url == f"s3://{BUCKET}/{key}"
    assert upload.url.startswith(f"https://{BUCKET}.s3")
    assert upload.fields["key"] == key
    assert upload.fields["Content-Type"] == "image/png"


def test_create_upload_limits_the_size_type_and_time_of_the_upload(s3):
    store = S3ImageStore(BUCKET, client=s3, upload_expiry_seconds=60)

    upload = store.create_upload(uuid4(), "puzzle14.jpg", 1024)

    policy = json.loads(base64.b64decode(upload.fields["policy"]))
    assert ["content-length-range", 1, 1024] in policy["conditions"]
    assert {"Content-Type": "image/jpeg"} in policy["conditions"]
    expiration = datetime.fromisoformat(policy["expiration"])
    assert expiration - datetime.now(UTC) <= timedelta(seconds=60)


def test_import_id_from_upload_key_returns_the_import_id():
    import_id = uuid4()

    assert import_id_from_upload_key(f"uploads/{import_id}/puzzle_14.png") == import_id


@pytest.mark.parametrize(
    "key",
    ["images/0b7f2d6e-0b7f-4d6e-8b7f-2d6e0b7f2d6e/puzzle.png", "uploads/not-a-uuid/puzzle.png", "uploads/puzzle.png"],
    ids=["other prefix", "invalid id", "missing folder"],
)
def test_import_id_from_upload_key_rejects_other_keys(key):
    with pytest.raises(ValueError):
        import_id_from_upload_key(key)
