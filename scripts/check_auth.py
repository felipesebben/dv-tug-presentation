import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.extract.bigquery_client import BigQuerySession

if __name__ == "__main__":
    load_dotenv()
    project_id = os.environ["BD_BILLING_PROJECT_ID"]

    session = BigQuerySession(billing_project=project_id)
    if session.ping():
        print("BigQuery connection ok.")
    else:
        print("Auth or billing project issue - check gcloud ADC and project id.")
