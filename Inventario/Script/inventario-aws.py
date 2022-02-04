import boto3
import pandas as pd
from openpyxl import Workbook
from pandas import ExcelWriter


def dataframe(data, path, name): 

    '''
    Crea un dataframe con la información entregada de cada cuenta y región
    Estos datos se envian a un documento excel en donde se almecena la información final
    '''
    
    df = pd.DataFrame(data=data)
    path = rf'{path}'
    with pd.ExcelWriter(path, mode='a') as writer:
        df.to_excel(writer, sheet_name=name)


def describe_instances(ec2, session, region, filename, profile):
    
    '''
    Extrae información relevante de las instancias EC2, luego la data se envía a la función: 
    dataframe
    '''
    
    ec2_resource = session.resource('ec2', region_name=region)

    image_id = []
    instance_id = []
    instance_type = []
    launch_time = []
    az = []
    private_dns = []
    public_dns = []
    state = []
    state_transition = []
    state_reason = [] 
    private_ip = []
    public_ip = [] 
    vpc_id = []
    subnet_id = []
    sg_name = []
    sg_id = []
    root_name = []
    root_type = []

    ec2_details = ec2.describe_instances()['Reservations']
    for g in ec2_details:
        instances = g['Instances']

        for i in instances:

            ami = i['ImageId']
            image_id.append(ami)
            ec2_id = i['InstanceId']
            instance_id.append(ec2_id)       
            ec2_type = i['InstanceType']
            instance_type.append(ec2_type)
            ec2_launch_time = i['LaunchTime']
            new_launch_time = ec2_launch_time.replace(tzinfo=None)
            launch_time.append(new_launch_time)        
            states = i['State']['Name']
            state.append(states)        
            transition_reason = i['StateTransitionReason']
            state_transition.append(transition_reason)              
            zones = i['Placement']['AvailabilityZone']
            az.append(zones)       
            priv_dns = i['PrivateDnsName']
            private_dns.append(priv_dns)        
            pub_dns = i['PublicDnsName']
            public_dns.append(pub_dns)
            root_device = i['RootDeviceName']
            root_name.append(root_device)
            root_dev_t = i['RootDeviceType']
            root_type.append(root_dev_t)

            if states != "terminated":            
                priv_ip = i['PrivateIpAddress']
                private_ip.append(priv_ip)
                vpc = i['VpcId']
                vpc_id.append(vpc)
                subnet = i['SubnetId']
                subnet_id.append(subnet)
                security_name = i['SecurityGroups'][0]['GroupName']
                sg_name.append(security_name)
                security_id = i['SecurityGroups'][0]['GroupId']
                sg_id.append(security_id)
                
            else:
                private_ip.append("")
                vpc_id.append("")
                subnet_id.append("")
                sg_name.append("")
                sg_id.append("")  

            if states == 'pending' or states == 'running':
                state_reason.append("")
            else:
                status_reason = i['StateReason']['Message']
                state_reason.append(status_reason)         

    for item in instance_id:

        instance = ec2_resource.Instance(item)
        pub_ip = instance.public_ip_address
        public_ip.append(pub_ip)
    
    if len(instance_id) != 0:
        ec2_data = { 
            'Image ID': image_id,
            'Instance ID': instance_id,
            'Instance Type': instance_type,
            'Launch Time': launch_time,
            'State': state,
            'State Reason': state_reason,
            'Transition Reason': state_transition,
            'Root Device Name': root_name,
            'Root Device Type': root_type,
            'Availability Zone': az,
            'VPC ID': vpc_id,
            'Subnet ID': subnet_id,
            'Private Ip Address': private_ip,
            'Private Dns Name': private_dns,
            'Public Ip Address': public_ip,
            'Public Dns Name': public_dns,
            'SG Name': sg_name,
            'SG Id': sg_id
            }

        path = filename # SNP-REGION
        name = 'EC2 Instances'
        dataframe(ec2_data, path, name)

    else:
        print(f"**No hay Instancias EC2 en la region {region} para la cuenta {profile}\n")

def describe_volumes(ec2, filename, region, profile):

    '''
    Extrae información relevante de los volumenes, luego la data se envía a la función: 
    dataframe
    '''

    volume_id = []
    volume_type = []
    size = []
    encrypted = []
    state = []
    creation_time = []
    az = []
    instance_id = []
    attach_time = []
    device_name = []
    delete_on_termination = []
    kms_key = []

    volumes_detail = ec2.describe_volumes()['Volumes']
    
    for v in volumes_detail:
            
        zones = v['AvailabilityZone']
        az.append(zones)
        size_gb = v['Size']
        size.append(size_gb)
        create_time = v['CreateTime']
        new_time = create_time.replace(tzinfo=None)
        creation_time.append(new_time)
        status = v['State']
        state.append(status)
        vol_id = v['VolumeId']
        volume_id.append(vol_id)
        vol_type = v['VolumeType']
        volume_type.append(vol_type)
        encryption = v['Encrypted']
        encrypted.append(encryption)

        if encryption:
            key_id = v['KmsKeyId']
            kms_key.append(key_id)
        else:
            kms_key.append("")
            
        attachment = v['Attachments']
        if attachment != []:
            attach = attachment[0]['AttachTime']
            new_attach = attach.replace(tzinfo=None)
            attach_time.append(new_attach)
            device = attachment[0]['Device']
            device_name.append(device)
            instance = attachment[0]['InstanceId']
            instance_id.append(instance)
            delete = attachment[0]['DeleteOnTermination']
            delete_on_termination.append(delete)       
        else:
            attach_time.append("")
            device_name.append("")
            instance_id.append("")
            delete_on_termination.append("") 
        
    if len(volume_id) != 0:
        volume_dict = {
            "Instance ID": instance_id,
            "Volume ID": volume_id,
            "Volume Type": volume_type,
            "Size GB": size,
            "Device Name": device_name,
            "State": state,
            "Attach Time": attach_time,
            "Encrypted": encrypted,
            "KMS Key": kms_key,
            "Delete On Termination": delete_on_termination,
            "Availavility Zone": az
            }
        path = filename
        name = 'Volumes'
        dataframe(volume_dict, path, name)

    else:
        print(f'**No hay volumenes en la región {region} para la cuenta {profile}\n')

def describe_images(ec2, account, filename, region, profile):

    '''
    Extrae información referente a las AMIs, luego la data se envía a la función: 
    dataframe

    '''

    images = ec2.describe_images(Owners=[str(account)])

    creation_date = []
    image_id = []
    image_location = []
    image_type = []
    public = []
    owner_id = []
    platform_detail = []
    state = []
    names = []
    description = []
    root_devicen = []
    root_devicet = []
    virtualization = []

    ami_detail = images['Images']

    for ami in ami_detail:

        creation = ami['CreationDate']
        creation_date.append(creation)
        ami_id = ami['ImageId']
        image_id.append(ami_id)
        source = ami['ImageLocation']
        image_location.append(source)
        ami_type = ami['ImageType']
        image_type.append(ami_type)
        public_bool = ami['Public']
        public.append(public_bool)
        owner = ami['OwnerId']
        owner_id.append(owner)
        platform = ami['PlatformDetails']
        platform_detail.append(platform)
        state_id = ami['State']
        state.append(state_id)
        name_id = ami['Name']
        names.append(name_id)
        descrip = ami['Description']
        description.append(descrip)
        device_name = ami['RootDeviceName']
        root_devicen.append(device_name)
        device_type = ami['RootDeviceType']
        root_devicet.append(device_type)
        virt = ami['VirtualizationType']
        virtualization.append(virt)

    if len(image_id) != 0:
        ami_data = {
            'Name': names,
            'Image ID': image_id,
            'Creation ID': creation_date,
            'Source': image_location,
            'Image Type': image_type,
            'Public': public,
            'Owner ID': owner_id,
            'Platform': platform_detail,
            'State': state,
            'Root Device Name': root_devicen,
            'Root Device Type': root_devicet,
            'Virtualization': virtualization,
            'Description': description
            }
        path = filename
        name = 'Images'
        dataframe(ami_data, path, name)

    else:
        print(f'**No hay Imagenes en la región {region} para cuenta {profile}\n')

def describe_snapshots(ec2, account, filename, region, profile):

    '''
    Extrae información refernte a los snapshots, luego la data se envía a la función: 
    dataframe
    '''

    description = []
    encrypted = []
    owner = []
    progress = []
    snapshot_id = []
    start_time = []
    state = []
    volume_id = []
    volume_size = []
    kms_key = []

    snapshots = ec2.describe_snapshots(OwnerIds=[str(account)])['Snapshots']

    for info in snapshots:

        descrip = info['Description']
        description.append(descrip)
        encryp = info['Encrypted']
        encrypted.append(encryp)
        owner_id = info['OwnerId']
        owner.append(owner_id)
        progress_= info['Progress']
        progress.append(progress_)
        snapshot = info['SnapshotId']
        snapshot_id.append(snapshot)
        start_time_ = info['StartTime']
        new_time = start_time_.replace(tzinfo=None)
        start_time.append(new_time)
        state_= info['State']
        state.append(state_)
        vol_id = info['VolumeId']
        volume_id.append(vol_id)
        vol_size = info['VolumeSize']
        volume_size.append(vol_size) 

        if encryp:
            key_id = info['KmsKeyId']
            kms_key.append(key_id)
        else:
            kms_key.append("")

    if len(snapshot_id) != 0:
        
        snapshot_data = {
            'Snapshot ID': snapshot_id,
            'Volume ID': volume_id,
            'Volume Size': volume_size,
            'Description': description,
            'State': state,
            'Start Time': start_time,
            'Progress': progress,
            'Encrypted': encrypted,
            'Kms Key': kms_key
            }
        path = filename
        name = 'Snapshots'
        dataframe(snapshot_data, path, name)

    else:
        print(f'**No hay Snapshots en la región {region} para la cuenta {profile}\n')

def describe_reserved_instances(ec2, filename, region, profile):

    '''
    Extrae información refernte a las instancias reservadas, luego la data se envía a la función: 
    dataframe

    '''

    duration = []
    end = []
    fixed_price = []
    instance_count = []
    instance_type = []
    product_description = []
    reserved_id = []
    start = []
    state = []
    usage_price = []
    currency = []
    tenancy = []
    offering_class = []
    offering_type = []
    recurring_charge = []
    frecuency_charge = []
    scope = []

    reserved_ec2 = ec2.describe_reserved_instances()['ReservedInstances']

    for item in reserved_ec2:
        
        duration_ = item['Duration']
        duration.append(duration_)
        end_time = item['End']
        new_end = end_time.replace(tzinfo=None)
        end.append(new_end)
        fixed_price_ = item['FixedPrice']
        fixed_price.append(fixed_price_)
        instance_count_ = item['InstanceCount']
        instance_count.append(instance_count_)
        instance_type_ = item['InstanceType']
        instance_type.append(instance_type_)
        product_description_ = item['ProductDescription']
        product_description.append(product_description_)
        reserved_id_ = item['ReservedInstancesId']
        reserved_id.append(reserved_id_)
        start_time = item['Start']
        new_start = start_time.replace(tzinfo=None)
        start.append(new_start)
        state_ = item['State']
        state.append(state_)
        usage_price_ = item['UsagePrice']
        usage_price.append(usage_price_)
        currency_code = item['CurrencyCode']
        currency.append(currency_code)
        instance_tenancy = item['InstanceTenancy']
        tenancy.append(instance_tenancy)
        offering_class_ = item['OfferingClass']
        offering_class.append(offering_class_)
        offering_type_ = item['OfferingType']
        offering_type.append(offering_type_)
        recurring_charge_a = item['RecurringCharges'][0]['Amount']
        recurring_charge.append(recurring_charge_a)
        frec_charge = item['RecurringCharges'][0]['Frequency']
        frecuency_charge.append(frec_charge)
        scope_ = item['Scope']
        scope.append(scope_)

    if len(reserved_id) != 0:
        reserved_data = {
            "Instance Type": instance_type,
            "Instance Count": instance_count,
            "Product Description": product_description,
            "Duration": duration,
            "Start Time": start,
            "End Time": end,
            "State": state,
            "Fixed Price": fixed_price,
            "Usage Price": usage_price,
            "Currency": currency,
            "Recurring Charge": recurring_charge,
            "Charge Frecuency": frecuency_charge,
            "Offering Type" : offering_type,
            "Offering Class": offering_class,
            "Reserved ID": reserved_id,
            "Instance Tenancy": instance_tenancy  
            }
        path = filename
        name = 'Reserved Instances'
        dataframe(reserved_data, path, name)

    else:
        print(f'**No hay Instancias reservadas en la región {region} para la cuenta {profile}\n')

def describe_elastic_ip(ec2, session, region, filename, profile):

    '''
    Extrae información refernte a las IP elasticas, luego la data se envía a la función: 
    dataframe

    '''

    ec2_resource = session.resource('ec2',  region_name=region)
    instances = []
    public_ip = [] 
    allocation = [] 
    association = []
    domain = [] 
    network_interface = []
    owner_id = []
    private_ip = []
    public_pool = [] 
    network_border_gp = [] 

    addresses = ec2.describe_addresses()['Addresses']

    for elastic in addresses: 
        ip = elastic['PublicIp']
        public_ip.append(ip)
        allo_id = elastic['AllocationId']
        allocation.append(allo_id)
        domain_id = elastic['Domain']
        domain.append(domain_id)
        pub_pool = elastic['PublicIpv4Pool']
        public_pool.append(pub_pool)
        network_border = elastic['NetworkBorderGroup']
        network_border_gp.append(network_border)
        
        eip = ec2_resource.VpcAddress(allo_id)
        ec2_id = eip.instance_id
        instances.append(ec2_id)
        association_ = eip.association_id
        association.append(association_)
        interface = eip.network_interface_id
        network_interface.append(interface)
        owner = eip.network_interface_owner_id
        owner_id.append(owner)
        priv_ip = eip.private_ip_address
        private_ip.append(priv_ip)

    if len(public_ip) != 0:
        eip_data = {
            "Instance ID": instances,
            "Elastic IP": public_ip,
            "Allocation ID": allocation,
            "Association ID": association,   
            "Domain": domain, 
            "Interface ID": network_interface,
            "Private IP": private_ip,
            "PublicIp Pool": public_pool,
            "Network Border Group": network_border_gp
            }
        path = filename
        name = 'Elastic IPs'
        dataframe(eip_data, path, name)

    else:
        print(f'**No hay IPs elasticas en la región {region} para la cuenta {profile}\n')

def describe_vpn(ec2, filename, region, profile):

    '''
    Extrae información refernte a las conexiones VPN, luego la data se envía a la función: 
    dataframe

    '''

    customer_gwids = [] 
    vpn_connection = [] 
    vpn_gateway = [] 
    state = [] 
    types = [] 
    tunnel1_state = [] 
    tunnel2_state =[] 

    vpn_connections = ec2.describe_vpn_connections()['VpnConnections']


    for vpn in vpn_connections:    
        customer_gw = vpn['CustomerGatewayId']
        customer_gwids.append(customer_gw)
        
        state_id = vpn['State']
        state.append(state_id) 
        
        type_id = vpn['Type']
        types.append(type_id)
        
        vpn_conn_id = vpn['VpnConnectionId']
        vpn_connection.append(vpn_conn_id)
        
        vpngw_id = vpn['VpnGatewayId']
        vpn_gateway.append(vpngw_id)
        
        tunnel1_status = vpn[ 'VgwTelemetry'][0]['Status']
        tunnel1_state.append(tunnel1_status)
        
        tunnel2_status = vpn[ 'VgwTelemetry'][1]['Status']
        tunnel2_state.append(tunnel2_status)

    if len(vpn_connection) != 0:

        vpn_data = {
            "VPN Connection": vpn_connection,
            "VPN Gateway": vpn_gateway,
            "Customer Gateway ID": customer_gwids,
            "State": state, 
            "Type": types,
            "Tunnel 1 Status": tunnel1_state,
            "Tunnel 2 Status": tunnel2_state
            }
        path = filename
        name = 'VPN Connections'
        dataframe(vpn_data, path, name)
        
    else:
       print(f'**No hay Conexiones VPN en la región {region} para la cuenta {profile}\n')

      
profiles_accounts = {
    'CHILE-VPC': 922813614730, 
    'CHILE': 354016829252, 
    'ARGENTINA': 776831313774, 
    'DELIVERY': 940618043275, 
    'SNP-LATAM': 885849409416
    }
regions = ['us-east-1', 'us-west-2', 'sa-east-1']

for profile in profiles_accounts:

    account = profiles_accounts[profile] 
    session = boto3.Session(profile_name=profile) 
    
    for region in regions:
        
        filename = f'{profile}\{profile}-{region}.xlsx'
        wb = Workbook()
        wb.save(filename = filename)
        
        ec2 = session.client('ec2', region_name=region)

        describe_instances(ec2, session, region, filename, profile)
        describe_volumes(ec2, filename, region, profile)
        describe_images(ec2, account, filename, region, profile)
        describe_snapshots(ec2, account, filename, region, profile)
        describe_reserved_instances(ec2, filename, region, profile)
        describe_elastic_ip(ec2, session, region, filename, profile)
        describe_vpn(ec2, filename, region, profile)