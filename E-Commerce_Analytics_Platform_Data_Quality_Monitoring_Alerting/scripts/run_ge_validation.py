import great_expectations as ge
from great_expectations.core.batch import RuntimeBatchRequest
import os
from sqlalchemy import create_engine
import sys

def run_ge_suite(table_name, suite_name):
    context = ge.get_context()
    engine = create_engine(os.getenv("GE_DB_CONN_STRING"))
    
    batch_request = RuntimeBatchRequest(
        datasource_name="postgres",
        data_connector_name="default_runtime_data_connector",
        data_asset_name=table_name,
        runtime_parameters={"query": f"SELECT * FROM {table_name}"},
        batch_identifiers={"table": table_name}
    )
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )
    results = validator.validate()
    if not results["success"]:
        raise Exception(f"GE validation failed for {table_name}: {results['statistics']}")
    return results