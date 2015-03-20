# Packstack-Install

This is a quick and dirty wrapper script to setup ansible, khaleesi for the
purpose of installing Packstack on an instance in an openstack cloud.

## Support
### Development Machine
Requires python 2.7


## How this works
This script will setup ansible on your development box and execute the setup of
Packstack.  Two nodes are launched one for the aio packstack, one for the tester node (tempest)

## Setup

Copy the packstack*  files to an empty directory.
```sh
mkdir /tmp/empty_dir
cp packstack* /tmp/empty_dir
```

Open the packstack-settings.sh file read the instructions and update the
settings appropriately.


## Usage

Once the settings are updated, simply execute the packstack-test.sh script

```sh
bash -x packstack-test.sh
```


