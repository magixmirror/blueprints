import os
import shipyard_utils as shipyard
import looker_sdk
from looker_sdk import api_settings

# create Artifacts folder paths
base_folder_name = shipyard.logs.determine_base_artifact_folder(
    'looker')
artifact_subfolder_paths = shipyard.logs.determine_artifact_subfolders(
    base_folder_name)
shipyard.logs.create_artifacts_folders(artifact_subfolder_paths)


class MyApiSettings(api_settings.ApiSettings):
    def __init__(self, *args, **kw_args):
        self.base_url = kw_args.pop('base_url')
        self.client_id = kw_args.pop("client_id")
        self.client_secret = kw_args.pop("client_secret")
        super().__init__(*args, **kw_args)

    def read_config(self):
        config = super().read_config()
        config['base_url'] = self.base_url
        config["client_id"] = self.client_id
        config["client_secret"] = self.client_secret
        # return config settings class
        return config


def get_sdk(base_url, client_id, client_secret):
    """Creates a looker v4.0 SDK for use in query methods
    
    Returns:
        sdk: Looker 4.0 SDK Class
    """
    # initialize looker sdk
    sdk = looker_sdk.init40(
    config_settings=MyApiSettings(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret
        )
    )
    return sdk

