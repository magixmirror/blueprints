import argparse
import sys
import time
import os
import shipyard_utils as shipyard
from looker_sdk import models
from looker_sdk.error import SDKError
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
    parser.add_argument('--dashboard-id', dest='dashboard_id', required=True)
    parser.add_argument('--output-width', dest='output_width', required=True)
    parser.add_argument('--output-height', dest='output_height', required=True)
    parser.add_argument('--destination-file-name', dest='dest_file_name', required=True)
    parser.add_argument('--destination-folder-name', dest='dest_folder_name', required=False)
    parser.add_argument('--file-type', dest='file_type',
                        choices=['pdf', 'png', 'jpg'],
                        type=str.lower,
                        required=True)
    args = parser.parse_args()
    return args


def download_dashboard(sdk, dashboard_id, width, height, file_format):
    """Download specified dashboard using ID
    
    Returns:
        result: raw binary data of the dashboard
    """
    try:
        task = sdk.create_dashboard_render_task(
            dashboard_id,
            file_format,
            models.CreateDashboardRenderTask(
                dashboard_style='tiled',
                dashboard_filters=None,
            ),
            width,
            height,
        )
    except:
        print("Error, the provided dashboard id was invalid. Please ensure that the dashboard id is correct.")
        sys.exit(ec.EXIT_CODE_INVALID_DASHBOARD_ID)

    if not (task and task.id):
        print(
            f'Could not create a render task for "{dashboard_id}"'
        )
        sys.exit(ec.EXIT_CODE_LOOK_DASHBOARD_ERROR)
    # poll the render task until it completes
    elapsed = 0.0
    delay = 0.5  # wait .5 seconds
    while True:
        poll = sdk.render_task(task.id)
        if poll.status == "failure":
            print(poll)
            print(
                f'Render failed for "{dashboard_id}"'
            )
            sys.exit(ec.EXIT_CODE_LOOK_DASHBOARD_ERROR)
        elif poll.status == "success":
            break

        time.sleep(delay)
        elapsed += delay
    print(f"Render task completed in {elapsed} seconds")

    result = sdk.render_task_results(task.id)
    return result



def main():
    args = get_args()
    base_url = args.base_url
    client_id = args.client_id
    client_secret = args.client_secret
    file_type = args.file_type
    dashboard_id = args.dashboard_id
    dest_file_name = args.dest_file_name
    dest_folder_name = args.dest_folder_name
    
    # get cwd if no folder name is specified
    if dest_folder_name is None or dest_folder_name == '':
        dest_folder_name = os.getcwd()
    ## create folder if it doesn't exist
    shipyard.files.create_folder_if_dne(dest_folder_name)
    destination_file_path = shipyard.files.combine_folder_and_file_name(
        dest_folder_name,
        dest_file_name
    )
    # generate SDK
    look_sdk = helpers.get_sdk(base_url, client_id, client_secret)
    
    # download look and write to file
    width = args.output_width
    height = args.output_height
    result = download_dashboard(look_sdk, dashboard_id, width, height, file_type)

    with open(destination_file_path, 'wb+') as f:
        f.write(result)
    print(f"file: {dest_file_name} created successfully")


if __name__ == "__main__":
    main()
    