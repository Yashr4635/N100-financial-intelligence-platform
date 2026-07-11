from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer


def test_normalizer_returns_dictionary():
    loader = ExcelLoader()
    datasets = loader.load_all()

    normalizer = DataNormalizer(datasets)
    clean = normalizer.normalize()

    assert isinstance(clean, dict)


def test_companies_not_empty():
    loader = ExcelLoader()
    datasets = loader.load_all()

    normalizer = DataNormalizer(datasets)
    clean = normalizer.normalize()

    assert len(clean["companies"]) > 0