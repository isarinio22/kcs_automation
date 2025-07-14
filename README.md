# KCS Report Automation

This project automates the extraction, transformation, analysis, and reporting of Knowledge-Centered Service (KCS) data, generating insightful PDF reports with charts and metrics for support operations.

## Project Structure

```
cli/           # Command-line interface entry points
config/        # Configuration files (e.g., Snowflake credentials)
data/          # Raw or intermediate data files (ignored by git)
output/        # Generated reports and charts (ignored by git)
src/
  extract/     # Data extraction from Snowflake
  transform/   # Data cleaning and metric calculations
  report/      # Report building and PDF export
  utils/       # Utility functions (e.g., logging)
  visualize/   # Chart and visualization functions
tests/         # Unit and integration tests
```

## Main Features
- **Automated Data Fetching:** Connects to Snowflake and fetches KCS articles and support cases for configurable date windows.
- **Data Cleaning & Metrics:** Cleans raw data and computes key KCS metrics (close reason ratios, median days to publish, etc.).
- **Visualizations:** Generates professional charts (pie, bar, line) using Plotly and Matplotlib.
- **PDF Report Generation:** Exports charts and insights into a formatted PDF report.
- **Configurable:** Uses environment variables for Snowflake credentials and settings.

## Getting Started

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd kcs_report
```

### 2. Install Dependencies
It is recommended to use a virtual environment.
```sh
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the `config/` directory with your Snowflake credentials:
```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_AUTHENTICATOR=snowflake
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

### 4. Run the Pipeline
You can run the main pipeline from the CLI or by executing the main script:
```sh
python -m cli.main
```
Or run the pipeline directly:
```sh
python src/pipeline.py
```

### 5. Output
- PDF reports and charts are saved in the `output/` directory.
- Raw/intermediate data is stored in `data/` (both are git-ignored).

## Testing
Run unit and integration tests with:
```sh
python -m unittest discover tests
```

## Extending & Customization
- Add new metrics in `src/transform/metrics.py`.
- Add or modify charts in `src/visualize/charts.py`.
- Update report templates in `src/report/template.md`.

## Dependencies
- Python 3.8+
- pandas
- plotly
- matplotlib
- fpdf
- snowflake-connector-python
- python-dotenv

See `requirements.txt` for the full list.

## License
MIT License

---

For questions or contributions, please open an issue or submit a pull request.
