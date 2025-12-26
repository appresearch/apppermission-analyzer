# AppPermission Analyzer

A comprehensive Python tool for analyzing application permission requests and patterns. Supports multiple platforms and provides detailed reports on permission usage, over-permissioning detection, and category-based analysis.

## Features

- Automated permission extraction from application metadata
- Pattern detection and anomaly identification
- Category-based permission analysis
- Export to multiple formats (CSV, JSON, PDF)
- Batch processing capabilities
- Support for Android and iOS applications

## Installation

```bash
pip install apppermission-analyzer
```

Or install from source:

```bash
git clone https://github.com/appresearch/apppermission-analyzer.git
cd apppermission-analyzer
pip install -e .
```

## Usage

### Basic Usage

```python
from apppermission_analyzer import Analyzer

analyzer = Analyzer()
results = analyzer.analyze("path/to/app.apk")
print(results.summary())
```

### Command Line

```bash
apppermission-analyzer analyze app.apk --output results.json
apppermission-analyzer batch apps/ --output batch_results/
apppermission-analyzer compare app1.apk app2.apk
```

## Requirements

- Python 3.8+
- aapt (Android Asset Packaging Tool) for Android analysis
- plistutil for iOS analysis (optional)

## License

MIT

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.


