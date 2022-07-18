import argparse
import sys
import os
import shipyard_utils as shipyard
try:
    import helpers
except BaseException:
    from . import helpers


EXIT_CODE_QUERY_ERROR = 203


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', dest='base_url', required=True)
    parser.add_argument('--client-id', dest='client_id', required=True)
    parser.add_argument('--client-secret', dest='client_secret', required=True)
    parser.add_argument('--query-id', dest='query_id', required=False)
    args = parser.parse_args()
    return args


def run_query_and_download(sdk, query_id, file_format):
    try:
        # Options are csv, json, json_detail, txt, html, md, xlsx, sql (raw query), png, jpg
        response = sdk.run_query(query_id=query_id, result_format=file_format)
        print("query {new_query.id} created successfully")
    except Exception as e:
        print(f'Error running create query: {e}')
        sys.exit(EXIT_CODE_QUERY_ERROR)
    return response


def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    file_type = args.file_type
    dest_file_name = args.dest_file_name
    dest_folder_name = args.dest_folder_name
    
    # get cwd if no folder name is specified
    if not dest_folder_name:
        dest_folder_name = os.getcwd()
    destination_file_path = shipyard.files.combine_folder_and_file_name(
        dest_folder_name,
        dest_file_name
    )
    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    if args.query_id:
        query_id = args.query_id
    else:
        artifact_subfolder_paths = helpers.artifact_subfolder_paths
        query_id = shipyard.logs.read_pickle_file(artifact_subfolder_paths, 
                                                    'query_id')
        
    # download look and write to file
    result = run_query_and_download(look_sdk, query_id, file_type)
    
    with open(destination_file_path, 'wb+') as f:
        f.write(result)
    print(f"query with file: {dest_file_name} created successfully!")


if __name__ == "__main__":
    main()