from airflow.models import DagBag
import pytest

def test_dag_loaded():
    dag_bag = DagBag()
    assert dag_bag.dags["sales_pipeline"] is not None
    assert len(dag_bag.import_errors) == 0

def test_dag_task_dependencies():
    dag = DagBag().dags["sales_pipeline"]
    tasks = dag.task_dict
    assert "generate_data" in tasks
    assert tasks["generate_data"].downstream_task_ids == {"ge_validation"}
    assert tasks["dbt_run"].upstream_task_ids == {"ge_validation"}
