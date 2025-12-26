"""
Command-line interface for apppermission-analyzer.
"""

import argparse
import json
import sys
from pathlib import Path
from .analyzer import Analyzer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze application permission requests and patterns"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an application")
    analyze_parser.add_argument("app_path", help="Path to application file")
    analyze_parser.add_argument(
        "--output", "-o", help="Output file path (JSON, CSV, or PDF)"
    )
    analyze_parser.add_argument(
        "--format", "-f", choices=["json", "csv", "txt"], default="json", help="Output format"
    )

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch analyze multiple applications")
    batch_parser.add_argument("apps_dir", help="Directory containing applications")
    batch_parser.add_argument("--output", "-o", help="Output directory")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two applications")
    compare_parser.add_argument("app1", help="First application")
    compare_parser.add_argument("app2", help="Second application")
    compare_parser.add_argument("--output", "-o", help="Output file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    analyzer = Analyzer()

    try:
        if args.command == "analyze":
            result = analyzer.analyze(args.app_path)
            output_data = result.to_dict()

            if args.output:
                output_path = Path(args.output)
                if args.format == "json" or output_path.suffix == ".json":
                    with open(output_path, "w") as f:
                        json.dump(output_data, f, indent=2)
                elif args.format == "csv" or output_path.suffix == ".csv":
                    # Simple CSV export
                    with open(output_path, "w") as f:
                        f.write("Permission,Category,Risk Level\n")
                        for perm in result.permissions:
                            f.write(f"{perm.name},{perm.category},{perm.risk_level}\n")
                else:
                    with open(output_path, "w") as f:
                        f.write(result.summary())
                print(f"Results saved to {args.output}")
            else:
                print(result.summary())
                if args.format == "json":
                    print(json.dumps(output_data, indent=2))

        elif args.command == "batch":
            apps_dir = Path(args.apps_dir)
            output_dir = Path(args.output) if args.output else Path("batch_results")
            output_dir.mkdir(exist_ok=True)

            app_files = list(apps_dir.glob("*.apk")) + list(apps_dir.glob("*.ipa"))
            print(f"Found {len(app_files)} applications to analyze")

            for app_file in app_files:
                try:
                    result = analyzer.analyze(str(app_file))
                    output_file = output_dir / f"{app_file.stem}.json"
                    with open(output_file, "w") as f:
                        json.dump(result.to_dict(), f, indent=2)
                    print(f"Analyzed: {app_file.name}")
                except Exception as e:
                    print(f"Error analyzing {app_file.name}: {e}")

        elif args.command == "compare":
            result1 = analyzer.analyze(args.app1)
            result2 = analyzer.analyze(args.app2)

            # Simple comparison
            perms1 = {p.name for p in result1.permissions}
            perms2 = {p.name for p in result2.permissions}

            common = perms1 & perms2
            only1 = perms1 - perms2
            only2 = perms2 - perms1

            comparison = {
                "app1": args.app1,
                "app2": args.app2,
                "common_permissions": list(common),
                "only_in_app1": list(only1),
                "only_in_app2": list(only2),
            }

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(comparison, f, indent=2)
                print(f"Comparison saved to {args.output}")
            else:
                print(json.dumps(comparison, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


