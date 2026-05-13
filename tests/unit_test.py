def test_api_key(api_key):
    assert api_key == "MOCK_KEY1234"
    
def test_channel_handle(channel_handle):
    assert channel_handle == "MOCK_HANDLE1234"
    
def test_connection(mock_connection):
    conn = mock_connection
    assert conn.host == "mockhost"
    assert conn.port == 1234
    assert conn.login == "user"
    assert conn.password == "password"
    assert conn.schema == "test_db"  
    
def test_dagbag(dagbag):
    assert dagbag.import_errors=={}, f"Import errors found: {dagbag.import_errors}"
    print("--------------------------------------")
    print(dagbag.import_errors)
    
    expected_dags = {'final_json', 'updated_db', 'data_quality_check'}
    loaded_dags = list(dagbag.dags.keys())
    print("--------------------------------------")
    print(dagbag.import_errors)
    
    for dag_id in expected_dags:
        assert dag_id in loaded_dags, f"DAG '{dag_id}' not found in DagBag. Loaded DAGs: {loaded_dags}"
        
    assert dagbag.size()== 3
    print("--------------------------------------")
    print(f"Total DAGs loaded: {dagbag.size()}")
    
    expected_tasks={
        'final_json': 3,
        'updated_db': 2,
        'data_quality_check': 2
    }
    print("--------------------------------------")
    
    for dag_id,dag in dagbag.dags.items():
        expected_count= expected_tasks[dag_id]
        actual_count= len(dag.tasks)
        assert actual_count == expected_count, f"DAG '{dag_id}' has {actual_count} tasks, expected {expected_count}"
        print(f"DAG '{dag_id}' has correct number of tasks: {actual_count}")
        
        
def test_mock_soda_check(mock_soda_check):
    from data_quality.soda import yt_elt_dq
    task = yt_elt_dq("test_schema")
    assert task == "Mocked Soda Check Task"

