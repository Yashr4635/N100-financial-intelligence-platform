from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer
from src.etl.validator import DataValidator


def main():
    loader = ExcelLoader()
    datasets = loader.load_all()

    normalizer = DataNormalizer(datasets)
    clean_data = normalizer.normalize()

    validator = DataValidator(clean_data)
    validator.validate()


if __name__ == "__main__":
    main()