import argparse

from pipeline import run_cli_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Research pipeline CLI")
    parser.add_argument("topic", help="Topic to research")
    parser.add_argument(
        "--api-key",
        required=True,
        help="Secret API key (set in .env or pass on the command line)",
    )
    args = parser.parse_args()

    try:
        run_cli_pipeline(args.topic, api_key=args.api_key)
    except PermissionError as exc:
        print(f"❌ Authentication failed: {exc}")
        exit(1)


if __name__ == "__main__":
    main()
