# rdo-manager images urls
-------------------------
##  Import images:

The following describe how the import images url should be map to be able to get
the correct url a product and a version.

The url for imports images is used in the role under:
    playbooks/installer/rdo-manager/roles/images/overcloud/import/tasks/main.yml
or
    playbooks/installer/rdo-manager/roles/images/undercloud/import/tasks/main.yml

    {{ installer.images.url[product.name][product.full_version][product.build][installer.images.version] }}{{ item }}.tar

So the installer.images.url is build with:
    product.name == [ 'rdo', 'rhos' ]
    product.full_version == [ '7-director', '8-director', 'liberty', 'mitaka',]
    product.build == ['ga', 'latest', 'last_known_good',]
    installer.images.version == ['7.1', '7.2', '8.0', 'latest', 'last_known_good',]

Note that the installer.images.version which is located under:
    product/{{ product.name }}/version/{{ product.version }}/build/
Correspond to the version of the product.
For rdo, this value is a lookup of the product.build value.
For rhos, this value is the version number of the product.
