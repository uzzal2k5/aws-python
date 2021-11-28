#!/usr/bin/env python
import boto3
from dateutil.parser import parse
import datetime
import argparse
import sys


# Get Input As an Argument----------
parser = argparse.ArgumentParser(description="AWS Arguments Parameters ")
parser.add_argument('--accountProfile', '-p', required=True)
parser.add_argument('--amiName', '-n', required=True)
parser.add_argument('--amiAge', '-a', type=int, required=True)
parser.add_argument('--isDelete', '-d', required=True)
args = parser.parse_args()


# AWS Account Profile
profile = args.accountProfile
session = boto3.Session(profile_name=profile)
client = session.client('ec2', region_name='eu-west-2')


# Calculate AMI Age
def ami_age_calculate(date):
    get_date_obj = parse(date)
    date_obj = get_date_obj.replace(tzinfo=None)
    diff = datetime.datetime.now() - date_obj
    return diff.days


# Get All AMI
amiName = args.amiName
AMI = client.describe_images(
    Filters=[
         {
           'Name': 'tag:Name',
           'Values': [amiName]
         } ]
    )

amiAge = args.amiAge
for amiID in AMI['Images']:
    CREATE_DATE = amiID['CreationDate']
    ami_age_days = ami_age_calculate(CREATE_DATE)
    if ami_age_days > amiAge:
        print( "IMAGE-ID : " + amiID['ImageId'] + " NAME : "+ amiID['Name'] + "| CREATION TIME : "+ amiID['CreationDate'] +'\n')

for ami in AMI['Images']:
    CREATE_DATE = ami['CreationDate']
    ami_age_days = ami_age_calculate(CREATE_DATE)
    if ami_age_days > amiAge:
        print( "IMAGE-ID : " + ami['ImageId'] + " NAME : "+ ami['Name'] +"| CREATION TIME : "+ ami['CreationDate']+ '\n')
        AMI_ID = ami['ImageId']
        deregister_ami = args.isDelete
        if deregister_ami.lower() == 'yes' or deregister_ami.lower() == 'y':
           print( "deleting -> " + AMI_ID + " - create_date = " + CREATE_DATE )
           client.deregister_image(ImageId=AMI_ID, DryRun=False)
        if deregister_ami.lower() == 'No' or deregister_ami.lower() == 'n' or  deregister_ami.lower() == '':
           print("Existing ..")
           sys.exit()
