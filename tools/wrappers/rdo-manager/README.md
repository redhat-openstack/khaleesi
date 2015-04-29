# RDO-Manager-Install

This is a quick and dirty wrapper script to setup ansible, khaleesi for the
purpose of installing RDO-Manager on a single bare metal machine.

## Support
### Development Machine
Requires python 2.7
### RDO-Manager Bare Metal Machine
https://repos.fedorapeople.org/repos/openstack-m/instack-undercloud/html/virt-setup.html#minimum-system-requirements


## How this works
This script will setup ansible on your development box and execute the setup of
RDO-Manager on the bare metal hardare specified in the rdo-manager-settings.sh

## Setup

Copy the rdo-manager*  files to an empty directory.

Open the rdo-manager-settings.sh file read the instructions and update the
settings appropriately.
```sh
mkdir /tmp/<dir>
cp rdo-manager* /tmp/<dir>
vi /tmp/<dir>/rdo-manager-settings.sh
```

## Usage

Once the settings are updated, simply execute the rdo-manager-test.sh script

```sh
chmod +x rdo-manager-test.sh
./rdo-manager-test.sh
```


