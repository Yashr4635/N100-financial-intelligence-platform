from src.loader import ExcelLoader


def main():
    loader = ExcelLoader()
    datasets = loader.load_all()

    print("\nDatasets loaded:")

    for name in datasets:
        print(f"- {name}")


if __name__ == "__main__":
    main()