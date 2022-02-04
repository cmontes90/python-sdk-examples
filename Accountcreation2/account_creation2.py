import boto3
import botocore
import sys
import json


session = boto3.Session(profile_name='A4L-MASTER')
client = session.client('organizations')

root_id = client.list_roots().get('Roots')[0].get('Id')


def create_ou(root_id, name='Default'):


    try:
        create_ou = client.create_organizational_unit(
                                Name=name,
                                ParentId=root_id)
        print(f'Organizational Unit: {name} has been successfully created')
        
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'DuplicateOrganizationalUnitException':
            print(f"The OU name '{name}' already exists, please try again")
        else:
            raise error

    with open('policy_cloudtrail.json') as file:
    #scp_content = json.dumps(file) 
    scp_content = file.read()
 
    scp_policy = client.create_policy(
    Content=scp_content,
    Description='Deny CloudTrail disable',
    Name='DenyCloudTrailDisable',
    Type='SERVICE_CONTROL_POLICY')

    list_scp_policies = client.list_policies(
    Filter='SERVICE_CONTROL_POLICY')

    scp_policy_id = list_scp_policies.get('Policies')[1].get('Id')


    return scp_policy_id
    
    
    #client.exceptions.DuplicateOrganizationalUnitException:
        #print(f'The OU name {name} already exists, please try again')
            

#create_ou(root_id, 'Shared Services')

with open('policy_cloudtrail.json') as file:
    #scp_content = json.dumps(file) 
    scp_content = file.read()

scp_policy = client.create_policy(
    Content=scp_content,
    Description='Deny CloudTrail disable',
    Name='DenyCloudTrailDisable',
    Type='SERVICE_CONTROL_POLICY')

list_scp_policies = client.list_policies(
    Filter='SERVICE_CONTROL_POLICY')

scp_policy_id = list_scp_policies.get('Policies')[1].get('Id')







