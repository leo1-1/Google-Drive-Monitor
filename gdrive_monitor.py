# pylint: disable=no-member
import argparse
import datetime
import logging
import os
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import rich.logging

_LOG_FMT = '%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s'
_LOG_FORMATTER = logging.Formatter(_LOG_FMT)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

logger = logging.getLogger()



def init_logger(logger: logging.Logger, log_level: str):
    logger.handlers = [rich.logging.RichHandler(rich_tracebacks=True)]
    logger.setLevel(getattr(logging, log_level.upper(), None))


def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf8') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def set_permissions_private(file, service, dry_run=False):
    # Print the file's name and permissions
    logger.info(f"File: {file['name']}")
    perm_str = ', '.join(f"{p['role']} ({p['type']})"
                         for p in file['permissions'])
    logger.info(f"Permissions: {perm_str}")

    if not file['shared']:
        return
    if dry_run:
        logger.info('Not changing permissions in dry run mode')
        return
    logger.info("Changing permission to private...")
    perms_to_remove = [p for p in file['permissions'] if p['role'] != 'owner']
    for perm in perms_to_remove:
        service.permissions().delete(fileId=file['id'],
                                     permissionId=perm['id']).execute()


def log_default_sharing_perms(service):
    response = service.about().get(fields='user').execute()
    permId = response['user']['permissionId']
    response = service.permissions().get(fileId='root',
                                         permissionId=permId).execute()
    logger.info('Default sharing settings: %s', response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-interval',
                        type=int,
                        default=3,
                        help='How often to check for new files')
    parser.add_argument('--log-level', type=str, default='INFO')
    parser.add_argument('--created-since',
                        type=str,
                        default=None,
                        help='Only check files created after this time')
    parser.add_argument('--no-dry-run',
                        action='store_false',
                        dest='dry_run',
                        help='Actually change the permissions of files')
    args = parser.parse_args()
    init_logger(logger, args.log_level)

    # Set up the Google Drive API service
    service = get_service()

    log_default_sharing_perms(service)

    # Set the datetime to use as the starting point for checking for new files
    if args.created_since:
        created_since = datetime.datetime.fromisoformat(args.created_since)
    else:
        created_since = datetime.datetime.now()

    files_processed = set()

    # Start an infinite loop to periodically check for new files
    while True:
        try:
            logger.info('Checking for new files...')
            # Get a list of all the files in the user's drive
            results = service.files().list(
                q="trashed = false",
                fields=("nextPageToken, files(id, name, createdTime, "
                        "modifiedTime, shared, permissions)")).execute()

            # Process each file in the drive
            for file in results.get('files', []):
                if file['id'] in files_processed:
                    continue
                files_processed.add(file['id'])
                # Check if the file was created after the last checked time
                modified_time = datetime.datetime.fromisoformat(
                    file['modifiedTime'][:-1])
                if modified_time > created_since:
                    set_permissions_private(file, service, args.dry_run)

            # Update the last checked time to the current time
            # created_since = datetime.datetime.now()

        except HttpError as error:
            logger.error(f"An error occurred: {error}")

        logger.info('Sleeping...')
        time.sleep(args.check_interval)


if __name__ == '__main__':
    main()
