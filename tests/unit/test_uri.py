from pytest import mark

from uncertainty_engine.uri import join_uri


@mark.parametrize(
    "parts, expect",
    [
        ([], ""),
        (["a"], "a"),
        (["a/"], "a"),
        (["a", "b"], "a/b"),
        (["a/", "b"], "a/b"),
        (["a", "/b"], "a/b"),
        (["a/", "/b"], "a/b"),
        (["a", "b", "c"], "a/b/c"),
        (["a/", "b", "c"], "a/b/c"),
        (["a", "/b", "c"], "a/b/c"),
        (["a", "b", "/c"], "a/b/c"),
        (["a/", "/b", "c"], "a/b/c"),
        (["a", "b/", "/c"], "a/b/c"),
        (["a", "", "c"], "a/c"),
    ],
)
def test_join_uri(parts: list[str], expect: str) -> None:
    result = join_uri(*parts)
    assert result == expect
