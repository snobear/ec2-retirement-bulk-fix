#!/usr/bin/env python
import boto3
import argparse
import datetime
import time
import sys

def stop_instance(instance_id, region):
    """
    Stop a given EC2 instance and wait until stopped
    """
    ec2 = boto3.resource('ec2', region_name=region)
    instance = ec2.Instance(instance_id)
    state = 'unknown'
    while not 'stopped' in state.lower():
        print( "Waiting for %s to stop..." % instance_id)
        response = instance.stop(Force=True)
        if response.get('StoppingInstances'):
            state = response['StoppingInstances'][0]['CurrentState']['Name']
        time.sleep(5)

    print( "%s new state: %s" % (instance_id,state))

def start_instance(instance_id, region):
    """
    Start a given EC2 instance and wait until running
    """
    ec2 = boto3.resource('ec2', region_name=region)
    instance = ec2.Instance(instance_id)
    state = 'unknown'
    while not 'running' in state.lower():
        print( "Waiting for %s to start..." % instance_id)
        response = instance.start()
        if response.get('StartingInstances'):
            state = response['StartingInstances'][0]['CurrentState']['Name']
        time.sleep(5)

    print( "%s new state: %s" % (instance_id,state))

def get_instance_name(instance_id, region):
    """
    When given an instance ID as str e.g. 'i-1234567', return the instance 'Name' from the name tag.
    """
    ec2_resource = boto3.resource('ec2', region_name=region)

    ec2instance = ec2_resource.Instance(instance_id)
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]
    return instancename

def get_instances(region, exclude_names=['master','search']):
    """
    Return a list of EC2 instances that have reboots scheduled in AWS
    """
    ec2 = boto3.client('ec2', region_name=region)

    filter_code = {
        'Name': 'event.code',
        'Values': ['instance-reboot','system-reboot','system-maintenance','instance-retirement','instance-stop']
    }
    statuses = ec2.describe_instance_status(Filters=[filter_code])
    instances = {}

    now = datetime.datetime.now()

    for s in statuses['InstanceStatuses']:
        _id = s['InstanceId']
        inst_name = get_instance_name(s['InstanceId'], region)
        instances[_id] = { 'name' : inst_name }

        for e in s['Events']:
            # exclude completed events and any excluded nodes
            event_date = e['NotBefore'].replace(tzinfo=None)
            excluded_by_name = any(x in inst_name.lower() for x in exclude_names)

            # unfortunately there is no status to denote completed events, so using description field
            if (event_date < now) or ('completed' in e['Description'].lower()) or excluded_by_name:
                if excluded_by_name:
                    print( "%s excluded due to the following name exclusions: %s" % (inst_name, exclude_names))
                del instances[_id]
                break

            instances[_id]['scheduled_date'] = e['NotBefore'].strftime('%m/%d/%Y')
            instances[_id]['code'] = e['Code']
            instances[_id]['description'] = e['Description']

    return instances

def list_instances(instances):
    """
    Print list of instance events
    """
    column_format = '{0: <25} {1: <20} {2: <15} {3: <14} {4: <40}'
    print( column_format.format('Name','ID','Event Code','Scheduled Date','Description'))
    for k,inst in instances.iteritems():
        print( column_format.format(inst['name'], k, inst['code'], inst['scheduled_date'], inst['description']))

if __name__ == '__main__':
    # set up params
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true', default=True, help='List instances with scheduled reboot events')
    parser.add_argument('-s', '--stopstart', action='store_true', default=False, help='Stop and start all instances with scheduled reboot events')
    parser.add_argument('-r', '--region', default='us-west-2', help='AWS Region, e.g. us-west-2')

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)

    region = args.region
    instances = get_instances(region)

    if len(instances) <= 0:
        print( 'There are no instances with scheduled events in region %s.' % region)
        sys.exit(0)

    list_instances(instances)

    if args.stopstart:
        choice = raw_input('\nThe above instances will be stopped and started. Continue? [y/n]:').lower()
        if choice not in ['yes','y']:
            print( 'Exiting, no changes made.')
            sys.exit(1)

        for instance_id,detail in instances.iteritems():
            stop_instance(instance_id, region)
            start_instance(instance_id, region)
