from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def test_all_locale_files_are_valid_yaml():
    for locale_file in (ROOT / 'locales').glob('*.yml'):
        with locale_file.open(encoding='utf-8') as stream:
            assert isinstance(yaml.safe_load(stream), dict), locale_file
