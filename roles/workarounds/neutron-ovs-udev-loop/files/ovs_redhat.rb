require "puppet"

Puppet::Type.type(:vs_port).provide(:ovs_redhat) do
  desc "Openvswitch port manipulation for RedHat family OSs"

  confine :osfamily => :redhat
  defaultfor :osfamily => :redhat

  optional_commands :vsctl => "/usr/bin/ovs-vsctl",
                    :sleep => "/bin/sleep"

  def exists?
    vsctl("list-ports", @resource[:bridge]).include? @resource[:interface]
  end

  def create
    if @resource[:keep_ip]
      create_physical_interface_file
      activate_port
    else
      vsctl("add-port", @resource[:bridge], @resource[:interface])
    end
  end

  def destroy
    vsctl("del-port", @resource[:bridge], @resource[:interface])
  end

  private

  def activate_port
    atomic_operation="ifdown #{@resource[:interface]};
      ovs-vsctl add-port #{@resource[:bridge]} #{@resource[:interface]};
      ifup #{@resource[:interface]};
      ifup #{@resource[:bridge]}"
    system(atomic_operation)
    sleep(@resource[:sleep]) if @resource[:sleep]
  end 

  def create_physical_interface_file
    file = File.open(Base + @resource[:interface], 'w+')
    file << "DEVICE=#{@resource[:interface]}\n"
    file << "DEVICETYPE=ovs\n"
    file << "TYPE=OVSPort\n"
    file << "BOOTPROTO=none\n"
    file << "OVS_BRIDGE=#{@resource[:bridge]}\n"
    file << "ONBOOT=yes\n"
    file.close
  end

  def search(file_name, value)
    File.open(file_name) { |file| 
      file.each_line { |line| 
        match = value.match(line)
        return match[0] if match
      }
    }
  end
    # The idea here to have a fixed MAC address
    datapath_id = vsctl("get", "bridge", @resource[:bridge], 'datapath_id')
    bridge_mac_address = datapath_id[-14..-3].scan(/.{1,2}/).join(':') if datapath_id

    if bridge_mac_address
      bridge_file << "OVS_EXTRA=\"set bridge #{@resource[:bridge]} other-config:hwaddr=#{bridge_mac_address}\"\n"
    end
    bridge_file.close
  end
end
