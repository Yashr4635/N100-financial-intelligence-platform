from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer


def main():
    loader = ExcelLoader()
    datasets = loader.load_all()

    normalizer = DataNormalizer(datasets)
    clean_data = normalizer.normalize()

    print("\nFinal Datasets")
    print("-" * 60)

    for name, df in clean_data.items():
        print(f"{name:<20}{df.shape}")


if __name__ == "__main__":
    main()
