"""Step 0.2 smoke test — verifies the package imports and pytest discovers tests."""


def test_package_imports() -> None:
    import modelgate

    assert modelgate is not None