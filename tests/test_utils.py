from src.utils import group_items


def test_group_items_never_exceeds_limit_when_items_fit():
    groups = group_items(['abc', 'de', 'fgh'], max_group_size=6, sep='|')

    assert groups == [('abc|de', ['abc', 'de']), ('fgh', ['fgh'])]
    assert all(len(text) <= 6 for text, _ in groups)
