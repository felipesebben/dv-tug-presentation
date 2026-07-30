"""Thin wrapper around basedosdados/BigQuery for querying and cost estimation."""

import pandas as pd
import basedosdados as bd
from google.cloud import bigquery
from pydata_google_auth import get_user_credentials

_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


class BigQuerySession:
    """Manages a billing project's connection to Base dos Dados' public BigQuery project."""

    def __init__(self, billing_project: str) -> None:
        self.billing_project = billing_project
        bd.config.billing_project_id = billing_project
        # basedosdados authenticates via its own cached pydata_google_auth token rather
        # than gcloud ADC, so the raw bigquery.Client used for dry runs needs the same
        # credentials explicitly, or it fails looking for ADC that was never set up.
        credentials = get_user_credentials(_SCOPES)
        self._client = bigquery.Client(project=billing_project, credentials=credentials)

    def ping(self) -> bool:
        """Runs a trivial query to confirm auth and billing project are set up correctly."""
        try:
            df = self.query("SELECT 1 AS ok")
            return int(df["ok"].iloc[0]) == 1
        except Exception as exc:
            print(f"Connection failed: {exc}")
            return False

    def estimate_bytes(self, query: str) -> int | None:
        """Dry-runs a query to get bytes processed, without executing or billing it.

        Returns None when BigQuery declines to estimate. This is not an edge case for
        this project: Base dos Dados' tables return None for every dry run, while
        Google's own public datasets return a real figure through the same client, so
        the limitation is in how BD shares its data, not in our setup. Callers must
        handle None explicitly rather than coercing it to 0 — a dry run that silently
        reports "0 MB" is worse than one that admits it doesn't know, because the whole
        point of the dry run is to catch an expensive query before it runs.

        When None comes back, size the query by hand from table metadata instead:
        `client.get_table(ref)` gives num_rows and num_bytes (both free to read), and
        bytes/row ÷ column count approximates the per-column cost.
        """
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = self._client.query(query, job_config=job_config)
        return job.total_bytes_processed

    def query(self, query: str) -> pd.DataFrame:
        """Executes a query and returns the result as a DataFrame."""
        return bd.read_sql(query, billing_project_id=self.billing_project)
