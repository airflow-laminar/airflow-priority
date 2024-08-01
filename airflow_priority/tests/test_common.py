def test_has_priority_tag(dag_run):
    from airflow_priority import has_priority_tag

    assert has_priority_tag(dag_run) == ("UNIT TEST", 1)
