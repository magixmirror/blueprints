import argparse
import sys
import os
import shipyard_utils as shipyard
try:
    import helpers
except BaseException:
    from . import helpers
try:
    import exit_codes as ec
except BaseException:
    from . import exit_codes as ec


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', dest='base_url', required=True)
    parser.add_argument('--client-id', dest='client_id', required=True)
    parser.add_argument('--client-secret', dest='client_secret', required=True)
    parser.add_argument('--look-id', dest='look_id', required=True)
    parser.add_argument('--destination-file-name', dest='dest_file_name', required=True)
    parser.add_argument('--destination-folder-name', dest='dest_folder_name', required=False)
    parser.add_argument('--file-type', dest='file_type',
                        choices=['json','txt','csv', 'json_detail', 'md', 'xlsx',
                                 'sql', 'png', 'jpg'],
                        type=str.lower,
                        required=True)
    args = parser.parse_args()
    return args


def download_look(look_sdk, look_id, file_format):
    all_looks = look_sdk.all_looks()
    all_look_ids = list(map(lambda x: x.id, all_looks))
    if look_id not in all_look_ids:
        print(f"The look id {look_id} does not exist, please provide a valid look id")
        sys.exit(ec.EXIT_CODE_INVALID_LOOK_ID)
    try:
        # Options are csv, json, json_detail, txt, html, md, xlsx, sql (raw query), png, jpg
        response = look_sdk.run_look(
        look_id=look_id,
        result_format=file_format
        )
        print(f"look {look_id} as {file_format} generated successfully")
    except Exception as e:
      print(f"Error running {look_id}: {e}")
      sys.exit(ec.EXIT_CODE_LOOK_ERROR)
    if type(response) == str:
        response = bytes(response, encoding='utf-8')
    return response


def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    file_type = args.file_type
    look_id = args.look_id
    dest_file_name = args.dest_file_name
    dest_folder_name = args.dest_folder_name
    
    # get cwd if no folder name is specified
    if not dest_folder_name:
        dest_folder_name = os.getcwd()
    else:
        shipyard.files.create_folder_if_dne(dest_folder_name)
    destination_file_path = shipyard.files.combine_folder_and_file_name(
        dest_folder_name,
        dest_file_name
    )
    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    
    # download look and write to file
    result = download_look(look_sdk, look_id, file_format=file_type)

    with open(destination_file_path, 'wb+') as f:
        f.write(result)


if __name__ == "__main__":
    main()
    