#!/usr/bin/env python
import boto3
from dateutil.parser import parse
import datetime
import argparse
import sys


# Get Input As an Argument----------
parser = argparse.ArgumentParser(description="AWS Arguments Parameters ")
parser.add_argument('--platform', '-o', required=True)
parser.add_argument('--accountProfile', '-p', required=True)
parser.add_argument('--amiName', '-n', required=True)
parser.add_argument('--amiAge', '-a', type=int, required=True)
parser.add_argument('--isDelete', '-d', required=True)
args = parser.parse_args()


# AWS Account Profile
profile = args.accountProfile
session = boto3.Session(profile_name=profile)
client = session.client('ec2', region_name='eu-west-2')

platform = args.platform
platform_input = ["windows", "linux"]

if platform not in platform_input:
    sys.exit("This is not a valid platform, please enter 'linux' or 'windows'")


# Calculate AMI Age
def ami_age_calculate(date):
    get_date_obj = parse(date)
    date_obj = get_date_obj.replace(tzinfo=None)
    diff = datetime.datetime.now() - date_obj
    return diff.days

# AMI Name
amiName = args.amiName
# Linux AMI Filters
linux_AMI = client.describe_images(
    Filters=[
            {
                'Name': 'tag:Name',
                'Values': [amiName]
            },
            {
                'Name': 'tag:Platform Name',
                'Values': ['Amazon Linux', 'Red Hat Enterprise Linux']
            }
    ]
)

# Windows AMI Filters
win_AMI = client.describe_images(
    Filters=[
            {
                'Name': 'tag:Name',
                'Values': [amiName]
           },
            {
                'Name': 'tag:Platform Name',
                'Values': ['Windows Server']
        }
    ]
)


snapshots = client.describe_snapshots(MaxResults=1000,OwnerIds=['self'])['Snapshots']

amiAge = args.amiAge

# Get All AMI List
def get_ami(amiAge,AMI):
    for amiID in AMI['Images']:
        CREATE_DATE = amiID['CreationDate']
        ami_age_days = ami_age_calculate(CREATE_DATE)
        if ami_age_days > amiAge:
            print( "IMAGE-ID : " + amiID['ImageId'] + " NAME : "+ amiID['Name'] + "| CREATION TIME : "+ amiID['CreationDate'] +'\n')

#Delete AMI & Associate  Snapshots
def delete_ami(amiAge,AMI,snapshots):
    for ami in AMI['Images']:
        CREATE_DATE = ami['CreationDate']
        ami_age_days = ami_age_calculate(CREATE_DATE)
        if ami_age_days > amiAge:
            print( "IMAGE-ID : " + ami['ImageId'] + " NAME : "+ ami['Name'] +"| CREATION TIME : "+ ami['CreationDate']+ '\n')
            AMI_ID = ami['ImageId']
            deregister_ami = args.isDelete
            if deregister_ami.lower() == 'yes' or deregister_ami.lower() == 'y':
               print( "deleting -> " + AMI_ID + " - create_date = " + CREATE_DATE )
               client.deregister_image(DryRun=False,ImageId=AMI_ID)
               for snapshot in snapshots:
                    if snapshot['Description'].find(AMI_ID) > 0:
                        client.delete_snapshot(SnapshotId=snapshot['SnapshotId'],DryRun=False)
                        print("Deleting snapshot {snapshot} \n".format(snapshot=snapshot['SnapshotId']))
            if deregister_ami.lower() == 'No' or deregister_ami.lower() == 'n' or  deregister_ami.lower() == '':
               print("Existing ..")
               sys.exit()


# Remove Linux AMI & Snapshots
if platform == "linux" and len(linux_AMI['Images']) >= 1:
    get_ami(amiAge,linux_AMI)
    delete_ami(amiAge,linux_AMI,snapshots)

# Remove Windows AMI & Snapshots
if platform == "windows" and len(win_AMI['Images']) >= 1:
    get_ami(amiAge,win_AMI)
    delete_ami(amiAge,win_AMI,snapshots)
