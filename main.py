
import json
from pathlib import Path

from analyzer import analyze_message


def main():
    message = input("Enter the customer message: ").strip()

    

    try:
        result = analyze_message(message)

        output_path = Path("output.json")
        output_path.write_text(
            json.dumps(result, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        print("\nAnalysis result:")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        print(f"\nSaved to: {output_path.resolve()}")

    except ValueError as error:
        print(f"Input error: {error}")


if __name__ == "__main__":
    main()