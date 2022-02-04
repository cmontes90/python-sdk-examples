import boto3
import botocore
import sys
import json

session = boto3.Session(profile_name='A4L-MASTER')
client = session.client('organizations')


def create_ou(root_ou, name='Shared Services'):
    
    try:
        if organization_unit_id is not None:
            move_account_to_ou = client.move_account(AccountId=account_id, SourceParentId=root_id, DestinationParentId=organization_unit_id)
        else:
            create_organizational_unit = client.create_organizational_unit(ParentId=root_ou, Name=name)

    except botocore.exceptions.ClientError as error:
        print(error)
        sys.exit(1)
    
    
    


def create_account(
        account_name,
        account_email,:
    
    try:
        create_account_response = client.create_account(
            Email=email,
            AccountName=account_name)
    except botocore.exceptions.ClientError as error:
        print(error)
        sys.exit(1)
    
  
    time.sleep(10)

    account_status = 'IN_PROGRESS'
    while account_status == 'IN_PROGRESS':

        create_account_status_response = client.describe_create_account_status(
        CreateAccountRequestId=create_account_response.get('CreateAccountStatus').get('Id'))
        print("Create account status "+str(create_account_status_response))

        account_status = create_account_response.get('CreateAccountStatus').get('State')

        if account_status == 'SUCCEEDED':
            account_id = create_account_status_response.get('CreateAccountStatus').get('AccountId')
            print(f'Account successfuly created, ID: {account_id}')

        else account_status == 'FAILED':
            account_failed = create_account_status_response.get('CreateAccountStatus').get('FailureReason)
            print(f'Account creation failed: {account_failed}')
            sys.exit(1)

    root_id = client.list_roots().get('Roots')[0].get('Id')
    return create_ou(root_id)
    
    
    if organization_unit_id is not None:
        # describe_ou = client.describe_organizational_unit(OrganizationalUnitId=organization_unit_id) 
        move_account_to_ou = client.move_account(AccountId=account_id, SourceParentId=root_id, DestinationParentId=organization_unit_id)
    
    else:
        create_ou(root_id, name)
    



    