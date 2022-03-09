PROJECT_ID = 'prj-inf-prodt-sharedvpchost'
BACKUP_REGION = 'us-central1'
BACKUP_RETENTION_TIME_HRS = 720

import google.auth
import google.auth.transport.requests
from google.auth.transport.requests import AuthorizedSession
import time
import requests
import json

credentials, project = google.auth.default()
request = google.auth.transport.requests.Request()
credentials.refresh(request)
authed_session = AuthorizedSession(credentials)

now = time.time()
retention_seconds = BACKUP_RETENTION_TIME_HRS * 60 * 60

def delete_backup(request):
    list = []
    trigger_run_url = "https://file.googleapis.com/v1beta1/projects/{}/locations/{}/backups".format(PROJECT_ID, BACKUP_REGION)
    r = authed_session.get(trigger_run_url)
    data = r.json()
    if not data:
        print("No backups to delete.")
    else:
        list.extend(data['backups'])
        while 'nextPageToken' in data.keys():
            nextPageToken = data['nextPageToken']
            trigger_run_url_next = "https://file.googleapis.com/v1beta1/projects/{}/locations/{}/backups?pageToken={}".format(PROJECT_ID, BACKUP_REGION, nextPageToken)
            r = authed_session.get(trigger_run_url_next)
            data = r.json()
            list.extend(data['backups'])
    for i in list:
        backup_time = i['createTime']
        backup_time = backup_time[:-4]
        backup_time = float(time.mktime(time.strptime(backup_time, "%Y-%m-%dT%H:%M:%S.%f")))
        if now - backup_time > retention_seconds:
            print("Deleting " + i['name'] + " in the background.")
            r = authed_session.delete("https://file.googleapis.com/v1beta1/{}".format(i['name']))
            data = r.json()
            print(data)
            if r.status_code == requests.codes.ok:
              print(str(r.status_code) + ": Deleting " + i['name'] + " in the background.")
            else:
              raise RuntimeError(data['error'])