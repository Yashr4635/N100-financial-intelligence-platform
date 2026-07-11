from src.etl.loader import ExcelLoader


def test_loader_returns_dictionary():
    loader = ExcelLoader()
    datasets = loader.load_all()

    assert isinstance(datasets, dict)
    assert len(datasets) == 12


def test_companies_loaded():
    loader = ExcelLoader()
    datasets = loader.load_all()

    assert "companies" in datasets
    assert len(datasets["companies"]) > 0