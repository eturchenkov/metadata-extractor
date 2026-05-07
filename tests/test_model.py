import pytest
from pydantic import ValidationError
from model import MetadataModel


VALID_FIELDS = {
    "page_id": "A1.01",
    "page_name": "Ground Floor Plan",
    "project_name": "City Library",
    "architect": "Jane Doe",
}


def test_valid_metadata():
    model = MetadataModel(**VALID_FIELDS)
    assert model.page_id == "A1.01"
    assert model.page_name == "Ground Floor Plan"
    assert model.project_name == "City Library"
    assert model.architect == "Jane Doe"


def test_model_dump_roundtrip():
    model = MetadataModel(**VALID_FIELDS)
    assert model.model_dump() == VALID_FIELDS


@pytest.mark.parametrize(
    "page_id",
    ["A1.01", "a-1", "A_1", "page.001", "A-1.01_v2", "1", "abc"],
)
def test_page_id_accepts_valid_pattern(page_id):
    model = MetadataModel(**{**VALID_FIELDS, "page_id": page_id})
    assert model.page_id == page_id


@pytest.mark.parametrize(
    "page_id",
    ["A 1.01", "A/1", "A#1", "page!", "A,1", "", "A1:01"],
)
def test_page_id_rejects_invalid_pattern(page_id):
    with pytest.raises(ValidationError):
        MetadataModel(**{**VALID_FIELDS, "page_id": page_id})


@pytest.mark.parametrize("field", list(VALID_FIELDS))
def test_missing_required_field_raises(field):
    fields = {k: v for k, v in VALID_FIELDS.items() if k != field}
    with pytest.raises(ValidationError):
        MetadataModel(**fields)


@pytest.mark.parametrize("field", list(VALID_FIELDS))
def test_none_field_raises(field):
    with pytest.raises(ValidationError):
        MetadataModel(**{**VALID_FIELDS, field: None})


def test_extra_fields_ignored_by_default():
    model = MetadataModel(**{**VALID_FIELDS, "unexpected": "ignored"})
    assert not hasattr(model, "unexpected")
