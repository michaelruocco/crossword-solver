import pytest

from crossword_solver_image.hash_factory import HashFactory


@pytest.fixture
def factory():
    return HashFactory()


def test_to_hash_string(factory):
    input_string = "hello"

    result = factory.to_hash(input_string)

    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_to_hash_bytes(factory):
    input_bytes = b"hello"

    result = factory.to_hash(input_bytes)

    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
