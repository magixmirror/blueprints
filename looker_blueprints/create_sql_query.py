import argparse
import sys
import shipyard_utils as shipyard
try:
    import helpers
except BaseException:
    from . import helpers
try:
    import exit_codes as ec
except BaseException:
    from . import exit_codes as ec
from looker_sdk import methods40, models40


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', dest='base_url', required=True)
    parser.add_argument('--client-id', dest='client_id', required=True)
    parser.add_argument('--client-secret', dest='client_secret', required=True)
    parser.add_argument("--connection-target", dest = 'connection_target',required = True,choices={"connection_name","model_name"})
    parser.add_argument("--connection-value", dest = 'connection_value', required=True)
    parser.add_argument('--sql', dest='sql', required=True)
    args = parser.parse_args()
    return args


def create_sql_query(look_sdk, connection_name, model_name, sql_query):
    sql_body = models40.SqlQueryCreate(
        connection_name=connection_name,
        model_name=model_name,
        sql=sql_query
    )
    try:
        res_slug = look_sdk.create_sql_query(
            body=sql_body
        ).slug
        print(f"Looker slug {res_slug} created successfully")
    except Exception as e:
        print(f'Error running create query: {e}')
        sys.exit(ec.EXIT_CODE_LOOK_QUERY_ERROR)
    return res_slug


def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    connection_target = args.connection_target
    connection_value = args.connection_value
    sql = args.sql

    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    
    # create sql query
    if connection_target == 'connection_name':
        sql_body = models40.SqlQueryCreate(connection_name= connection_value,model_name=None ,sql = sql)

    elif connection_target == 'model_name':
        sql_body = models40.SqlQueryCreate(model_name= connection_value, connection_name= None ,sql= sql)
    
    try:
        new_slug = look_sdk.create_sql_query(body = sql_body).slug
        print(f"Looker slug {new_slug} created successfully")
        # save slug to pickle file
        artifact_subfolder_paths = helpers.artifact_subfolder_paths
        shipyard.logs.create_pickle_file(artifact_subfolder_paths, 
                                                    'slug', new_slug)

    except Exception as e:
        print(f"Error running create query: {e}")
        sys.exit(ec.EXIT_CODE_LOOK_QUERY_ERROR)
    

if __name__ == "__main__":
    main()
    