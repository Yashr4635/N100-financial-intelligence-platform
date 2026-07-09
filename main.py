from src.loader import ExcelLoader


def main():

    loader = ExcelLoader()

    datasets = loader.load_all()

    print("\nDataset Summary")
    print("-" * 70)

    for name, df in datasets.items():

        print(
            f"{name:<20}"
            f"{df.shape[0]:>6} rows"
            f"{df.shape[1]:>6} cols"
        )


if __name__ == "__main__":
    main()