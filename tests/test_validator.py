from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer
from src.etl.validator import DataValidator


def test_validator_runs():
    loader = ExcelLoader()
    datasets = loader.load_all()

    normalizer = DataNormalizer(datasets)
    clean = normalizer.normalize()

    validator = DataValidator(clean)
    validator.validate()

    assert isinstance(validator.failures, list)


def test_validation_report_created():
    import os

    assert os.path.exists("reports/validation_failures.csv")
