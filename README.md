### About

This script allows you to:

- List all AWS EC2 instances that are scheduled for retirement in a given region
- Do a bulk stop and start of these instances (so that they are migrated to new hardware)

You could use this to automate handling of instance retirements. Or to make life easier if you manage many EC2 instances and thus get a ton of retirement notices at once.

### Install

```
git clone https://github.com/snobear/ec2-retirement-bulk-fix.git
cd ec2-retirement-bulk-fix
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage

Set your AWS access key and secret

```
export AWS_ACCESS_KEY_ID="KEY-GOES-HERE"
export AWS_SECRET_ACCESS_KEY="secret"
```

**List instances scheduled for retirement**

```
./retired.py --region us-west-2 --list
```

**Stop and start instances scheduled for retirement**

This will stop and start all instances one at a time:

```
./retired.py --region us-west-2 --stopstart
```

**Excluding instances**

You can optionally ignore instances by name. Currently, this is hardcoded in, so anything you want to exclude by name can be added to the `exclude_names` list in this function in the script:

```
def get_instances(region, exclude_names=['master','search']):
```

A PR would be appreciated to parameterize this :).

**Help**

```
./retired.py --help
```

### About EC2 Instance Retirements

Occasionally, you'll receive a notice from AWS that your EC2 instance is scheduled for retirement. Per [AWS docs](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-retirement.html), 

> An instance is scheduled to be retired when AWS detects irreparable failure of the underlying hardware hosting the instance. When an instance reaches its scheduled retirement date, it is stopped or terminated by AWS. If your instance root device is an Amazon EBS volume, the instance is stopped, and you can start it again at any time. Starting the stopped instance migrates it to new hardware. If your instance root device is an instance store volume, the instance is terminated, and cannot be used again.

### Contributing

Issues and pull requests are quite welcome.
