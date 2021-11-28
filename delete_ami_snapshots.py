#!/usr/bin/env python3
import boto3
from dateutil.parser import parse
import datetime
import argparse
import sys

# Get Input As an Argument----------
parser = argparse.ArgumentParser(description="AWS Arguments Parameters ")
parser.add_argument('--accountProfile', '-p', required=True)
parser.add_argument('--snapName', '-n', required=True)
parser.add_argument('--snapAge', '-a', type=int, required=True)
parser.add_argument('--isDelete', '-d', required=True)
args = parser.parse_args()

# AWS Account Profile
profile = args.accountProfile
session = boto3.Session(profile_name=profile)
client = session.client('ec2', region_name='eu-west-2')


# Calculate Snapshots Age
def snap_age_calculate(date):
    get_date_obj = parse(date)
    date_obj = get_date_obj.replace(tzinfo=None)
    diff = datetime.datetime.now() - date_obj
    return diff.days


# Get Snapshots Source List
def get_snapshots_src(snapName):
     response = client.describe_snapshots(OwnerIds=['self'],Filters=[{'Name': 'tag:Name', 'Values': [snapName]}])
     return response['Snapshots']

# Snapshots Name
snapName = args.snapName
snapshots = get_snapshots_src(snapName)


# Get All Snapshots List
def get_snapshots(snapAge,snapshots):
    for snap  in snapshots:
        for tag in snap['Tags']:
            if tag['Key'] == 'Name':
               SNAP_NAME = tag['Value']
        START_TIME = snap['StartTime'].isoformat()
        snap_age_days = snap_age_calculate(START_TIME)
        if snap_age_days > snapAge:
            print( "SNAPSHOTS ID : " + snap['SnapshotId'] + " NAME : "+ SNAP_NAME + "| START TIME : "+ snap['StartTime'] +'\n')

# Snapshots Name
snapAge = args.snapAge
get_snapshots(snapAge,snapshots)

# Deleting Snapshots
for snap in snapshots:
    for tag in snap['Tags']:
        if tag['Key'] == 'Name':
            SNAP_NAME = tag['Value']
    START_TIME = snap['StartTime'].isoformat()
    snap_age_days = snap_age_calculate(START_TIME)
    try:
        if snap_age_days > snapAge:
           SNAP_ID = snap['SnapshotId']
           delete_snap = args.isDelete
           if delete_snap.lower() == 'yes' or delete_snap.lower() == 'y':
              print("Deleting snapshot {snap} \n".format(snap=snap['SnapshotId']) + "Name ", SNAP_NAME)
              client.delete_snapshot(SnapshotId=snap['SnapshotId'],DryRun=False)
           if delete_snap.lower() == 'No' or delete_snap.lower() == 'n' or  delete_snap.lower() == '':
              print("Not Deleting Any Snapshots ..")
              sys.exit()
    except Exception(e):
        if 'InvalidSnapshot.InUse' in e.message:
           print("skipping this snapshot ", snap['SnapshotId'])
           continue



