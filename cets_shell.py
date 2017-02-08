from cmd2 import Cmd, make_option, options
import optparse
import nova_instance_provisioning as provision
import pop_discover as discover
import nova_instance_delete as delete
import nova_instance_shutdown as shutdown
import nova_instance_start as start
import nova_instance_pause as pause
import nova_instance_unpause as unpause
import nova_instance_suspend as suspend
import nova_instance_resume as resume
import nova_instance_reboot as reboot
import fault_injection as fault_inject
import network_stats_collection as net_stats
import get_flavor_list as flavorlist
import get_hypervisor_list as hypervisorlist
import get_image_list as imagelist
import get_keypair_list as keypairlist
import get_instance_list as instancelist
import ceilometer_statistics as ceilostats
import nova_create_keypair as add_keypair
import get_vnc_console as vncconsole 
import heat_instance_provisioning as hprovision 
import nova_create_flavor as flavor 
import nova_autoscaling as scaling 
import get_host_list as hlist
import get_host_details as hdetails
import neutron_net_create as net_create
import neutron_get_list as net_list
import neutron_net_delete as net_delete
import neutron_subnet_list as subnet_list
import neutron_subnet_create as subnet_create
import neutron_subnet_delete as subnet_delete
import neutron_get_port_list as port_list
import neutron_port_delete as port_delete
import neutron_port_create as port_create 
import storage_statistics as storage
import storage_statistics_sysbench as storage_sys

 
class Commands(Cmd):
 
    # The docstring of the method serves as the 'help' for the
    # command as well, eg., when query as: help foo
    def check_params(self, d):
        '''Confirm that no values in dictionary d are None.'''

        # Plain Jane style:
        '''
        res = True
        noparams = []
        for k, v in d.items():
            if not v:                          # Same as:: if v is None: ?
                noparams.append(k)
                res = False
        return res, noparams
        '''
        # Tarzan style'''
        noparams = filter(lambda k: d[k] is None, d)
        return len(noparams) == 0, noparams


    def translate_keys(self, d, keys):
        return ', '.join(map(lambda k: ('%s=%s' % (keys[k], d[k])), d))


    def dict_to_discovery_cmd(self, d):
        discovery_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, discovery_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name')
    ])
    def do_discovery(self, args, opts=None):
        """please provide following parameters
           With this command you can do the discovery of no. of pop's.
           and the corresponding image list, flavor list, keypair list, instance list, hypervisor list of related pop
        The input parameters are:

            The PoP name, from where you want to delete VM.
            The instance id,    Id of the instance you want to delete.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'discover ' + self.dict_to_discovery_cmd(d)
            print('Cmd line: %s' % cmdline)
            with open('discovery.txt','w+') as f:
                f.write(cmdline)
            discover.discovery('discovery.txt') 
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_provision_cmd(self, d):
        provision_keys = {
            'image': 'os_image_name',
            'flavor': 'flavor_type',
            'pop': 'pop_name',
            'instance': 'instance_name',
            'keypair': 'keypair_key',
            'net_id': 'net_id'
        }
        return self.translate_keys(d, provision_keys) 



    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--image', type='string', help='Image Name'),
        make_option('-f', '--flavor', type='string', help='Flavor Name'),
        make_option('-k', '--keypair', type='string', help='Keypair Name'),
        make_option('-n', '--instance', type='string', help='instance Name'),
        make_option('-N', '--net_id', type='string', help='network id',default=0)
    ])
    def do_provision(self, args, opts=None):
        '''
        With this command you can provision a VM.

        The input parameters are:

            The PoP name, so that the newly created PoP is easily recognizable.
            The OS image name, with which to bring up the VM.
            Flavor are the parameters for the VM.
            Keypair is the authentication parameter for the client to access the VM.
            Instance name is the name given to VM.'''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
	    cmdline = 'provision ' + self.dict_to_provision_cmd(d) 
            print('Cmd line: %s' % cmdline)
             
            with open('provision.txt','w+') as f: 
                f.write(cmdline)                            
            provision.nova_provision('provision.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
    

    def dict_to_stop_cmd(self, d):
        stop_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, stop_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_stop(self, args, opts=None):
        """please provide following parameters
           With this command you can deprovision the instance in given PoP name.

        The input parameters are:

            The PoP name, from where you want to delete VM.
            The instance id,    Id of the instance you want to delete.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'shutdown ' + self.dict_to_stop_cmd(d)
            print('Cmd line: %s' % cmdline)
            with open('stop_instance.txt','w+') as f:
                f.write(cmdline)
            shutdown.shutdown_instance('stop_instance.txt')
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_start_cmd(self, d):
        start_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, start_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_start(self, args, opts=None):
        """please provide following parameters
           With this command you can start the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to START VM.
            The instance id, Id of the instance you want to start.   

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'start ' + self.dict_to_start_cmd(d)
            print('Cmd line: %s' % cmdline)
            with open('start_instance.txt','w+') as f:
                f.write(cmdline)
            start.start_instance('start_instance.txt')
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_pause_cmd(self, d):
        pause_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, pause_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_pause(self, args, opts=None):
        """please provide following parameters
           With this command you can pause the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to pause VM.
            The instance id, Id of the instance you want to pause.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'pause ' + self.dict_to_pause_cmd(d)
            print('Cmd line: %s' % cmdline)
            with open('pause_instance.txt','w+') as f:
                f.write(cmdline)
            pause.pause_instance('pause_instance.txt')
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_unpause_cmd(self, d):
        unpause_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, unpause_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_unpause(self, args, opts=None):
        """please provide following parameters
           With this command you can unpause the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to unpause VM.
            The instance id, Id of the instance you want to unpause.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'unpause ' + self.dict_to_unpause_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('unpause_instance.txt','w+') as f:
                f.write(cmdline)
            unpause.unpause_instance('unpause_instance.txt')
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_suspend_cmd(self, d):
        suspend_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, suspend_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_suspend(self, args, opts=None):
        """please provide following parameters
           With this command you can suspend the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to suspend VM.
            The instance id, Id of the instance you want to suspend.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'suspend ' + self.dict_to_suspend_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('suspend_instance.txt','w+') as f:
                f.write(cmdline)
            suspend.suspend_instance('suspend_instance.txt') 
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))



    def dict_to_resume_cmd(self, d):
        resume_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, resume_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_resume(self, args, opts=None):
        """please provide following parameters
           With this command you can resume the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to resume VM.
            The instance id, Id of the instance you want to resume.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'resume ' + self.dict_to_resume_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('resume_instance.txt','w+') as f:
                f.write(cmdline)
            resume.resume_instance('resume_instance.txt') 
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_reboot_cmd(self, d):
        reboot_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, reboot_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_reboot(self, args, opts=None):
        """please provide following parameters
           With this command you can reboot the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to reboot VM.
            The instance id, Id of the instance you want to reboot.

           <pop name> Name of the pop
           <server> Name or ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'reboot ' + self.dict_to_reboot_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('reboot_instance.txt','w+') as f:
                f.write(cmdline)
            reboot.reboot_instance('reboot_instance.txt') 
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_delete_cmd(self, d):
        delete_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, delete_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_delete(self, args, opts=None):
        """please provide following parameters
           With this command you can deprovision the instance in given PoP name.

        The input parameters are:

            The PoP name, from where you want to delete VM.
            The instance id, 	Id of the instance you want to delete.      
            
           <pop name> Name of the pop
           <server>  ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
	    cmdline = 'delete ' + self.dict_to_delete_cmd(d) 
            print('Cmd line: %s' % cmdline)
             
            with open('deprovision.txt','w+') as f: 
                f.write(cmdline)                            
            delete.delete_instance('deprovision.txt')
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
      
 
    def dict_to_fault_inject_cmd(self, d):
        fault_inject_keys = {
            'pop': 'pop_name',
            'fault': 'fault_type',
            'compute_ip': 'compute_ip_address',
            'port': 'port',
            'instance': 'instance_id'
        }
        return self.translate_keys(d, fault_inject_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-f', '--fault', type='string', help='fault type'),
        make_option('-c', '--compute_ip', type='string', help='compute ip address'),
        make_option('-n', '--port', type='string', help='port number'),
        make_option('-i', '--instance', type='string', help='instance id')
    ])
    def do_fault_inject(self, args, opts=None):
        """please provide following parameters
           With this command you can reboot the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to reboot VM.
            The instance id, Id of the instance you want to reboot.
            The fault type, It specifies the type of fault ex. VM_CRASH.
            The compute_ip, Compute node IP address where we want to inject fault. 
            The port number,Port number of the compute node.
            The instance id, Id of the instance in which we want to inject fault.    
           """
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'inject-fault ' + self.dict_to_fault_inject_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('fault_inject.txt','w+') as f:
                f.write(cmdline)
            fault_inject.inject_fault('fault_inject.txt')
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))



    def dict_to_network_fault_inject_cmd(self, d):
        network_fault_inject_keys = {
            'pop': 'pop_name',
            'fault': 'fault_type',
            'compute_ip': 'compute_ip_address',
            'port': 'port',
            'interface': 'interface_name',
            'action': 'action',
        }
        return self.translate_keys(d, network_fault_inject_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-f', '--fault', type='string', help='fault type'),
        make_option('-c', '--compute_ip', type='string', help='compute ip address'),
        make_option('-n', '--port', type='string', help='port number'),
        make_option('-i', '--interface', type='string', help='interface name'),
        make_option('-a', '--action', type='string', help='action down or up')
    ])
    def do_network_fault_inject(self, args, opts=None):
        """please provide following parameters
           With this command you can reboot the instance in given PoP name.

        The input parameters are:

            The PoP name, Where you want to reboot VM.
            The instance id, Id of the instance you want to reboot.
            The fault type, It specifies the type of fault ex. network_fault.
            The compute_ip, Compute node IP address where we want to inject fault.
            The port number,Port number of the compute node.
            The interface name, name of the instance(tap interface) in which we want to inject fault.
            The action, action to perform wheather it's up or down 	.
           """
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'inject-fault ' + self.dict_to_network_fault_inject_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('network_fault_inject.txt','w+') as f:
                f.write(cmdline)
            fault_inject.inject_network_fault('network_fault_inject.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_network_stats_cmd(self, d):
        network_stats_keys = {
            'pop': 'pop_name',
            'url': 'url'
        }
        return self.translate_keys(d, network_stats_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name'),
        make_option('-u', '--url', type='string', help='openday light url')
    ])
    def do_network_stats(self, args, opts=None):
        """please provide following parameters
           With this command you can get the network flow stats in a given PoP name.

        The input parameters are:

            The PoP name, from where you want to delete VM.
            The url, url of openday light to get network flow stats.


           <pop name> Name of the pop
           <url>  ID of server"""
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'collect networks stats ' + self.dict_to_network_stats_cmd(d)
            print('Cmd line: %s' % cmdline)

            with open('network_stats.txt','w+') as f:
                f.write(cmdline)
            net_stats.network_stats('network_stats.txt') 
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    def dict_to_flavor_list_cmd(self, d):
        flavor_keys = {
            'pop': 'pop_name',
        }
        return self.translate_keys(d, flavor_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose flavors are required.')
    ])
    def do_flavor_list(self, args, opts=None):
        '''
        With this command you can determine the flavors in given PoP name.

        The input parameters are:

            The PoP name, whose flavors are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'flavor_list ' + self.dict_to_flavor_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('flavorlist.txt','w+') as f:
                f.write(cmdline)
            flavorlist.get_flavor_list('flavorlist.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


     
    '''
    def dict_to_flavor_create_cmd(self, d):
         flavor_keys = {
             'pop': 'pop_name',
             'name': 'flavor_name',
             'id': 'flavor_id',
             'ram': 'ram_size',
             'disk': 'disk_size',
             'vcpus': 'no_of_vcpus',
             'rxtx': 'rxtxfactor',
             'ephemeral': 'ephemeral',
             'public': 'ispublic',
             'swap': 'swap'
         }
         return self.translate_keys(d, flavor_keys)

    @options([
        make_option('-n', '--name', type='string', help='Name of the new flavor'),
        make_option('-i', '--id', type='string', help='Unique ID for the flavor'),
        make_option('-r', '--ram', type='string', help='Memory size in MB'),
        make_option('-d', '--disk', type='string', help='Disk size in GB'),
        make_option('-v', '--vcpus', type='string', help='Number of VCPUs'),
        make_option('-e', '--ephemeral', type='string', help='Ephemeral space size in GB', default='0'),
        make_option('-s', '--swap', type='string', help='Swap space size in GB', default='0'),
        make_option('-f', '--rxtx', type='string', help='RX / TX Factor', default='1'),
        make_option('-p', '--public', type='string', help='Make flavor accessible to the public', default='true')
    ])
    def do_flavor_create(self, args, opts=None):
         With this command you can create the new flavor in given PoP name.

         The input parameters are:

            The Flavor name, ID, RAM Size, Disk Size, Number of vcpus whose flavors are required.
         d = vars(opts)
         print ('d')
         print d
         parse_status, missing_params = self.check_params(vars(opts))
         if parse_status:
             cmdline = 'flavor_create ' + self.dict_to_flavor_create_cmd(d)
             print('Cmd line:\n%s' % cmdline)
             print 'The dict', d
         else:
             print('The missing parameters are: %s' % ', '.join(missing_params))

    '''



    def dict_to_image_list_cmd(self, d):
        image_keys = {
            'pop': 'pop_name',
        }
        return self.translate_keys(d, image_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose images are required.')
    ])
    def do_image_list(self, args, opts=None):
        '''
        With this command you can list the images in given PoP name.

        The input parameters are:

            The PoP name, whose flavors are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'image_list ' + self.dict_to_image_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('imagelist.txt','w+') as f:
                f.write(cmdline)
            imagelist.get_image_list('imagelist.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    ''' 
    def dict_to_image_create_cmd(self, d):
         image_keys = {
             'pop': 'pop_name',
             'server': 'server_name',
             'snapshot': 'snapshot_name'
         }
         return self.translate_keys(d, image_keys)

    @options([
        make_option('-i', '--server', type='string', help='Name or ID of the server'),
        make_option('-s', '--snapshot', type='string', help='Name of the snapshot')
    ])
    def do_image_create(self, args, opts=None):
         
         With this command you can create the new image in given PoP name.

         The input parameters are:

            The server name or ID and snapshot name.
         
         d = vars(opts)
         print ('d')
         print d
         parse_status, missing_params = self.check_params(vars(opts))
         if parse_status:
             cmdline = 'image_create ' + self.dict_to_image_create_cmd(d)
             print('Cmd line:\n%s' % cmdline)
             print 'The dict', d
         else:
             print('The missing parameters are: %s' % ', '.join(missing_params))
    '''




    def dict_to_hypervisor_list_cmd(self, d):
        hypervisor_keys = {
            'pop': 'pop_name',
        }
        return self.translate_keys(d, hypervisor_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose images are required.')
    ])
    def do_hypervisor_list(self, args, opts=None):
        '''
        With this command you can list the hypervisor in given PoP name.

        The input parameters are:

            The PoP name, whose flavors are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'hypervisor_list ' + self.dict_to_hypervisor_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('hypervisorlist.txt','w+') as f:
                f.write(cmdline)
            hypervisorlist.get_hypervisor_list('hypervisorlist.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
 

    def dict_to_keypair_list_cmd(self, d):

        keypair_keys = {
            'pop': 'pop_name',
        }
        return self.translate_keys(d, keypair_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose images are required.')
    ])
    def do_keypair_list(self, args, opts=None):
        '''
        With this command you can list the keypair in given PoP name.

        The input parameters are:

            The PoP name, whose keypairs are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'keypair_list ' + self.dict_to_keypair_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('keypairlist.txt','w+') as f:
                f.write(cmdline)
            keypairlist.get_keypair_list('keypairlist.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_keypair_add_cmd(self, d):
        keypair_keys = {
            'pop': 'pop_name',
            'keypair': 'keypair_name'
        }
        return self.translate_keys(d, keypair_keys)

    @options([
        make_option('-k', '--keypair', type='string', help='keypair name to be created.'),
        make_option('-p', '--pop', type='string', help='PoP Name where we want to create keypair required.')
    ])
    def do_keypair_add(self, args, opts=None):
        '''
        With this command you can add the keypair in given PoP name.

        The input parameters are:

            The PoP name and keypair name are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'create ' + self.dict_to_keypair_add_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('add_keypair.txt','w+') as f:
                f.write(cmdline)
            add_keypair.create_keypair('add_keypair.txt')
            

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))



    def dict_to_instance_list_cmd(self, d):
        instance_keys = {
            'pop': 'pop_name',
        }
        return self.translate_keys(d, instance_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose instance are required.')
    ])
    def do_instance_list(self, args, opts=None):
        '''
        With this command you can list the instance in given PoP name.

        The input parameters are:

            The PoP name, whose instances are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'instance_list ' + self.dict_to_instance_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('instancelist.txt','w+') as f:
                f.write(cmdline)
            instancelist.get_instance_list('instancelist.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_ceilometer_stats_cmd(self, d):
        ceilometer_keys = {
            'pop': 'pop_name',
            'meter': 'meter_name'
        }
        return self.translate_keys(d, ceilometer_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-m', '--meter', type='string', help='Meter Name whose statistics are required.')
    ])
    def do_ceilometer_stats(self, args, opts=None):
        '''
        With this command you can display the metering statistics in given PoP name.

        The input parameters are:

            The PoP name, whose instances are required.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'ceilometer_stats ' + self.dict_to_ceilometer_stats_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('ceilometerstats.txt','w+') as f:
                f.write(cmdline)
            ceilostats.collect_statistics('ceilometerstats.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
 


    def dict_to_vncconsole_cmd(self, d):
        console_keys = {
            'pop': 'pop_name',
            'instance': 'instance_id',
            'console': 'console_type'
        }
        return self.translate_keys(d, console_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-i', '--instance', type='string', help='instance id.'),
        make_option('-c', '--console', type='string', help='Type of console.')
    ])
    def do_vncconsole_url(self, args, opts=None):
        '''
        With this command you can display console in web url of given instance & PoP name.

        The input parameters are:

            The instance id, whose console we want to see in url are required.
            The console type, type of console.
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'vncconsole ' + self.dict_to_vncconsole_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('vncconsole.txt','w+') as f:
                f.write(cmdline)
            vncconsole.get_vnc_console('vncconsole.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    
    def dict_to_heat_provision_cmd(self, d):
        heat_provision_keys = {
            'pop': 'pop_name',
            'template': 'yaml_file',
            'stack': 'stack_name'
        }
        return self.translate_keys(d, heat_provision_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-y', '--template', type='string', help='yaml/heat template .'),
        make_option('-s', '--stack', type='string', help='stack name.')
    ])
    def do_create_instance(self, args, opts=None):
        '''
        With this command you can provision a vm using heat template in a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.
            The heat template, 
            The stack name, 
        ''' 
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            cmdline = 'provision ' + self.dict_to_heat_provision_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('heat_provision.txt','w+') as f:
                f.write(cmdline)
            hprovision.heat_provision('heat_provision.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    
    def dict_to_create_flavor_cmd(self, d):
        create_flavor_keys = {
            'pop': 'pop_name',
            'name': 'name',
            'memory_mb': 'ram',
            'vcpus': 'vcpus',
            'disk_gb': 'disk' 
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, create_flavor_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-n', '--name', type='string', help='Name of the flavor .'),
        make_option('-r', '--memory_mb', type='string', help='Memory size in MB.'),
        make_option('-c', '--vcpus', type='string', help='Number of vcpus.'),
        make_option('-d', '--disk_gb', type='string', help='Disk size in GB.'),
    ])
    def do_create_flavor(self, args, opts=None):
        '''
        With this command you can create a new flavor in a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.
            The name of the flavor 
            The memory in mb
            The vcpus
            The disk space in gb 
              
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            print 'd:',d
            cmdline = 'create-flavor ' + self.dict_to_create_flavor_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('create_flavor.txt','w+') as f:
                f.write(cmdline)
            flavor.create_flavor('create_flavor.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
 
    def dict_to_host_list_cmd(self, d):
        host_list_keys = {
            'pop': 'pop_name',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, host_list_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose host list is required.'),
    ])
    
    def do_host_list(self, args, opts=None):
        '''
        With this command you can get the host list in a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.
              
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'host-list ' + self.dict_to_host_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('host_lists.txt','w+') as f:
                f.write(cmdline)
            hlist.get_host_list('host_lists.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
    
    def dict_to_host_details_cmd(self, d):
        host_details_keys = {
            'pop': 'pop_name',
	    'host': 'host'
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, host_details_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose host details is required.'),
        make_option('-q', '--host', type='string', help='Name of host whose details is required.'),
    ])
    def do_host_details(self, args, opts=None):
        ''' 
        With this command you can get the host list in a given PoP name.

        The input parameters are:

            The PoP name, whose host list is required.
	    The Host Name, whose details is required 
              
        ''' 
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'host-details ' + self.dict_to_host_details_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('host_details.txt','w+') as f:
                f.write(cmdline)
            hdetails.get_host_details('host_details.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
        
    def dict_to_autoscale_cmd(self, d):
        autoscale_keys = {
            'pop': 'pop_name',
            'instance_id': 'instance_id',
            'flavor': 'flavor_name',
            'compute_ip': 'compute_ip',
            'port': 'port', 
            'wait_time': 'wait_time',
            'cycles': 'cycles',
            'stats': 'stats', 
            'cpu_threshold': 'cpu_add_threshold'
        }
        #print '&&&&&&&&&&:',self.translate_keys(d, autoscale_keys)
        
        return self.translate_keys(d, autoscale_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name where auto-scaling will be enabled.'),
        make_option('-i', '--instance_id', type='string', help='Id of the instance to be enabled for auto-scaling.'),
        make_option('-f', '--flavor', type='string', help='Flavor name to be used for new instance.'),
        make_option('-C', '--compute_ip', type='string', help='IP address of compute node.'),
        make_option('-P', '--port', type='string', help='Port for the socket.'),
        make_option('-t', '--wait_time', type='string', help='Time between two consecutive cpu% request.'),
        make_option('-c', '--cycles', type='string', help='Number of times the cpu% should be checked against the threshold.'),
        make_option('-s', '--stats', type='string', help='Resource of machine for which statistics will be collected from the plugin.'),
        make_option('-T', '--cpu_threshold', type='string', help='Threshold for cpu%.'),
    ])
    def do_auto_scaling(self, args, opts=None):
        '''
        With this command you can enable autoscaling for an instance in a given PoP name.

        The input parameters are:

             PoP Name where auto-scaling will be enabled.
             Id of the instance to be enabled for auto-scaling.
             Flavor name to be used for new instance.
             IP address of compute node.
             Port for the socket.
             Time between two consecutive cpu% request.
             Number of times the cpu% should be checked agianst the threshold.
             Resource of machine for which statistics will be collected from the plugin.
             Threshold for cpu%. 
        '''
        d1 = vars(opts)
        d2={} 
        d3 ={}
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd1:',d1
            d2['stats'] = d1.pop('stats') 
            d3['cpu_threshold'] = d1.pop('cpu_threshold')
            #print 'd2&d3:****',d2,'\n',d3
            #print 'd1:',d1
            cmdline1 = 'get-stats ' + self.dict_to_autoscale_cmd(d1)+'\n'
            cmdline2 = 'collect ' + self.dict_to_autoscale_cmd(d2)+'\n'
            cmdline3 = self.dict_to_autoscale_cmd(d3)
            #print('Cmd line1:\n%s' % cmdline1)
            #print('Cmd line2:\n%s' % cmdline2)
            #print('Cmd line3:\n%s' % cmdline3)

            with open('auto-scaling.txt','w+') as f:
                f.write(cmdline1)
                f.write(cmdline2)
                f.write(cmdline3)
            scaling.auto_scaling('auto-scaling.txt')
            #print '*****'
        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_create_network_cmd(self, d):
        create_network_keys = {
            'pop': 'pop_name',
            'network_name': 'network_name',
            'network_type': 'network_type',
            'phy_net_name': 'phy_net_name',
            'segmentation_id': 'segmentation_id'
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, create_network_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name .'),
        make_option('-n', '--network_name', type='string', help='Name of the network .'),
        make_option('-t', '--network_type', type='string', help='Type of the network', default='local'),
        make_option('-s', '--segmentation_id', type='string', help='segmentation id', default=0),
        make_option('-l', '--phy_net_name', type='string', help='name of the physical network', default=0),
    ])
    def do_create_network(self, args, opts=None):
        '''
        With this command you can create a new flavor in a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.
            The network name 
            The type of network ex gre,vlan,flat etc 
            The segmentation id 
            The physical network name 

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'create-network ' + self.dict_to_create_network_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('create_network.txt','w+') as f:
                f.write(cmdline)
            net_create.neutron_net_create('create_network.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_net_list_cmd(self, d):
        get_net_list_keys = {
            'pop': 'pop_name',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, get_net_list_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
    ])
    def do_net_list(self, args, opts=None):
        '''
        With this command you can get a network listin  a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'net-list ' + self.dict_to_net_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('net_list.txt','w+') as f:
                f.write(cmdline)
            net_list.neutron_get_list('net_list.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    def dict_to_net_delete_cmd(self, d):
        net_delete_keys = {
            'pop': 'pop_name',
            'network_id': 'network_id',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, net_delete_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-i', '--network_id', type='string', help='Id of the network to be delete.'),
    ])
    def do_net_delete(self, args, opts=None):
        '''
        With this command you can get a network listin  a given PoP name.

        The input parameters are:

            The PoP name, from where we want to do delete network.
            The network id,Id of the network we want to delete.

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'net-delete ' + self.dict_to_net_delete_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('net_delete.txt','w+') as f:
                f.write(cmdline)
            net_delete.delete_network('net_delete.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    def dict_to_subnet_list_cmd(self, d):
        get_subnet_list_keys = {
            'pop': 'pop_name',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, get_subnet_list_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
    ])
    def do_subnet_list(self, args, opts=None):
        '''
        With this command you can get a network listin  a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'subnet-list ' + self.dict_to_subnet_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('subnet_list.txt','w+') as f:
                f.write(cmdline)
            subnet_list.neutron_subnet_list('subnet_list.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_create_subnet_cmd(self, d):
        create_subnet_keys = {
            'pop': 'pop_name',
            'network_name': 'network_name',
            'cidr': 'cidr',
            'subnet_name': 'subnet_name',
            'ip_version': 'ip_version'
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, create_subnet_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-n', '--network_name', type='string', help='Name of the network .'),
        make_option('-c', '--cidr', type='string', help=' network'),
        make_option('-s', '--subnet_name', type='string', help='Name of the subnet'),
        make_option('-i', '--ip_version', type='string', help='name of the physical network', default=4),
    ])
    def do_create_subnet(self, args, opts=None):
        '''
        With this command you can create a new flavor in a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.
            The name of the network 
            The cidr address range 
            The subnet name 
            The ip version 

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'create-subnet ' + self.dict_to_create_subnet_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('create_subnet.txt','w+') as f:
                f.write(cmdline)
            subnet_create.neutron_subnet_create('create_subnet.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_subnet_delete_cmd(self, d):
        subnet_delete_keys = {
            'pop': 'pop_name',
            'subnet_id': 'subnet_id',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, subnet_delete_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-i', '--subnet_id', type='string', help='Id of the subnet to be delete.'),
    ])
    def do_subnet_delete(self, args, opts=None):
        '''
        With this command you can get a network listin  a given PoP name.

        The input parameters are:

            The PoP name, from where we want to do delete network.
            The subnet id,Id of the subnetnetwork we want to delete.

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'subnet-delete ' + self.dict_to_subnet_delete_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('subnet_delete.txt','w+') as f:
                f.write(cmdline)
            subnet_delete.delete_subnet('subnet_delete.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))


    def dict_to_virt_top_cmd(self, d):
        virt_top_keys = {
            'pop': 'pop_name',
            'instance_id': 'instance_id',
            'compute_ip': 'compute_ip',
            'port': 'port',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, virt_top_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name.'),
        make_option('-i', '--instance_id', type='string', help='Id of the instance .'),
        make_option('-c', '--compute_ip', type='string', help='Compute ip'),
        make_option('-s', '--port', type='string', help='port no.'),
    ])
    def do_get_io_stats(self, args, opts=None):
        '''
        With this command you can get the storage statistics for an instance in a given PoP name.

        The input parameters are:

            The PoP name .
            The Id of the instance
            The Ip of compute node 
            The port no.

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'storage-stats ' + self.dict_to_virt_top_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('virt_top.txt','w+') as f:
                f.write(cmdline)
            storage.vm_storage_stats('virt_top.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    def dict_to_port_list_cmd(self, d):
        get_port_list_keys = {
            'pop': 'pop_name',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, get_port_list_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name .'),
    ])
    def do_port_list(self, args, opts=None):
        '''
        With this command you can get a port list in a given PoP name.

        The input parameters are:

            The PoP name .

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'port-list ' + self.dict_to_port_list_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('port_list.txt','w+') as f:
                f.write(cmdline)
            port_list.neutron_get_port_list('port_list.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

    def dict_to_create_port_cmd(self, d):
        create_port_keys = {
            'pop': 'pop_name',
            'network_name': 'network_name',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, create_port_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name whose metering statistics are required.'),
        make_option('-n', '--network_name', type='string', help='Name of the network .'),
    ])
    def do_create_port(self, args, opts=None):
        '''
        With this command you can create a new flavor in a given PoP name.

        The input parameters are:

            The PoP name, where we want to do provision.
            The name of the network

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'create-port ' + self.dict_to_create_port_cmd(d)
            print('Cmd line:\n%s' % cmdline)

            with open('create_port.txt','w+') as f:
                f.write(cmdline)
            port_create.neutron_port_create('create_port.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))

 
    def dict_to_port_delete_cmd(self, d):
        port_delete_keys = {
            'pop': 'pop_name',
            'port_id': 'port_id',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, port_delete_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name.'),
        make_option('-i', '--port_id', type='string', help='Id of the port to be delete.'),
    ])
    def do_port_delete(self, args, opts=None):
        '''
        With this command you can delete the port in a given PoP name.

        The input parameters are:

            The PoP name, from where we want to do delete network.
            The port id,Id of the port we want to delete.

        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'port-delete ' + self.dict_to_port_delete_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('port_delete.txt','w+') as f:
                f.write(cmdline)
            port_delete.delete_port('port_delete.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))
    
    def dict_to_storage_stats_cmd(self, d):

        storage_stats_keys = {
            'pop': 'pop_name',
            'action': 'action',
            'compute_ip': 'compute_ip',
            'port': 'port',
            'instance_ip': 'instance_ip',
            'oltp_table_size': 'oltp_table_size',
        }
        #print '&&&&&&&&&&:', self.translate_keys(d, create_flavor_keys)
        return self.translate_keys(d, storage_stats_keys)

    @options([
        make_option('-p', '--pop', type='string', help='PoP Name.'),
        make_option('-a', '--action', type='string', help='Action to be perform	.'),
        make_option('-c', '--compute_ip', type='string', help='Ip of compute node'),
        make_option('-n', '--port', type='string', help='Port number.'),
        make_option('-i', '--instance_ip', type='string', help='Instance ip.', default='None' ),
        make_option('-s', '--oltp_table_size', type='string', help='size.', default=0 ),
    ])
    def do_get_storage_stats(self, args, opts=None):
        '''   
        With this command you can delete the port in a given PoP name.

        The input parameters are:

            The PoP name, from where we want to do delete network.
            The action to be perform
            The ip of compute node 
            The port number
            The instance ip
            The table size
        '''
        d = vars(opts)
        parse_status, missing_params = self.check_params(vars(opts))
        if parse_status:
            #print 'd:',d
            cmdline = 'storage-stats ' + self.dict_to_storage_stats_cmd(d)
            print('Cmd line:\n%s' % cmdline)
            with open('storage_stats.txt','w+') as f:
                f.write(cmdline)
            storage_sys.vm_storage_stats_sysbench('storage_stats.txt')

        else:
            print('The missing parameters are: %s' % ', '.join(missing_params))



  
 
    def do_shell(self, line):
        print("Shell call with: ", line);
        pass
 
    def we_are_done(self):
        import sys
        sys.exit()


 
def main():
    commands = Commands()
    commands.intro = '\nThis is the CETS command processor. Version 0.1.61803398875.\n'
    commands.prompt = 'cets-shell> '
    commands.cmdloop()
 
if __name__ == '__main__':
    main()
 
 

