import vastdb
import pyarrow as pa

def connect_to_vastdb(endpoint, access_key, secret_key):
    """Connects to VastDB."""
    try:
        session = vastdb.connect(endpoint=endpoint, access=access_key, secret=secret_key)
        # print("Connected to VastDB")
        return session
    except Exception as e:
        raise RuntimeError(f"Failed to connect to VastDB: {e}") from e

def write_to_vastdb(session, bucket_name, schema_name, table_name, pa_table):
    """Writes data to VastDB."""
    with session.transaction() as tx:
        bucket = tx.bucket(bucket_name)
        schema = bucket.schema(schema_name, fail_if_missing=False) or bucket.create_schema(schema_name)

        table = schema.table(table_name, fail_if_missing=False) or schema.create_table(table_name, pa_table.schema)

        columns_to_add = get_columns_to_add(table.arrow_schema, pa_table.schema)
        for column in columns_to_add:
            table.add_column(column)

        table.insert(pa_table)

def get_columns_to_add(existing_schema, desired_schema):
    """Identifies columns to add to an existing schema."""
    existing_fields = set(existing_schema.names)
    desired_fields = set(desired_schema.names)
    return [pa.schema([pa.field(name, desired_schema.field(name).type)]) for name in desired_fields - existing_fields]
