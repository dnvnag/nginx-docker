'''
Below code snippet is for getting the image list from the server.
'''

import json
import httplib2
import urllib
from novaclient import utils
import prettytable
import strutils 

def generate_record(str):
    '''
    Parse:
    provision pop_name = pop1, pop2 
    '''
    str = str.strip()
    words = str.split('=')
    record = {}
    parts = words[1].split(',')
    for i in xrange(len(parts)):
        parts[i] = parts[i].strip()    
    return parts

def determine_configuration():
    lines = []
    with open('cets-server.config', 'r') as f:
        lines = f.readlines()
    config = {}
    for line in lines:
        xline = line.strip()
        if xline == '':
            continue
        sa = xline.split('=')
        #print ('sa :%s' % sa)
        config[sa[0].strip()] = sa[1].strip()
    #print config
    return config

def invoke_remote_test(record_as_json, configuration):
    '''this function will invoke remote method using REST API'''
    connection = httplib2.Http(".cache")
    headers = { "content-type": "application/x-www-form-urlencoded" }
    #print 'jsonpayload********:', record_as_json
    params = urllib.urlencode({ 'jsonpayload': record_as_json })
    #print 'params:************\n', params
    (response, content) = connection.request(configuration['instance.url'],
        'GET', headers=headers, body=params)
    #print('Resonse status: reason##### %s: %s' % (response.status, response.reason))
    return response, content

def save_instance(content):
    file_name = 'instance.info'
    with open(file_name, 'a+') as f:
        f.write(content+' ') 
        f.write('\n')	

def get_keystone_creds(pop_config_file):
    #print "pop file name: %s \n" % pop_config_file
    d = {}
    try:
    	with open(pop_config_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                #print 'lines:********\n', line
                line = line.strip()
                #print 'lstrip(line):********\n', line
                if line.startswith('pop-keystone-access'):
                    d['keystone_auth_url'] = line.split('=')[1].lstrip()
                elif line.startswith('OS_USERNAME'):
                    d['os_username'] = line.split('=')[1].lstrip()
                elif line.startswith('OS_PASSWORD'):
                    d['password'] = line.split('=')[1].lstrip()
                elif line.startswith('OS_TENANT_NAME'):
                    d['tenant_id'] = line.split('=')[1].lstrip()
    except IOError as e:
        print e
    return d

def print_table(objs, fields, formatters={}, sortby_index=None):
    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    mixed_case_fields = ['serverId']
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                #data = getattr(o, field_name, '')
                #data = o[field_name]
                if field_name == 'networks' and o.get('addresses', '').get('private', '')!= '':
                    data = 'private=' + o.get('addresses', '').get('private', '')[0].get('addr','')
                elif field_name == 'networks' and o.get('addresses', '').get('public', '')!= '': 
                    data = 'public=' + o.get('addresses', '').get('public', '')[0].get('addr','')
                elif field_name == 'networks' and o.get('addresses', '').get('vepc', '')!= '': 
                    data = 'vepc=' + o.get('addresses', '').get('vepc', '')[0].get('addr','')
                elif field_name == 'networks' and o.get('addresses', '').get('epc-network', '')!= '': 
                    data = 'epc-network=' + o.get('addresses', '').get('epc-network', '')[0].get('addr','')
                elif field_name == 'networks': 
                    data = '-' 
                else:
		    if field_name == 'task_state':
   		    	field_name = 'OS-EXT-STS:task_state'
                    elif field_name == 'power_state':
   		    	field_name = 'OS-EXT-STS:power_state'
		    data = o.get(field_name, '')
                    if field_name == 'OS-EXT-STS:power_state' and data == 1:
 		        data = 'Running'
                    elif field_name == 'OS-EXT-STS:power_state' and data == 4:
                        data = 'Shutdown'
                    elif field_name == 'OS-EXT-STS:power_state' and data == 3: 
                        data = 'Paused'
                if data is None:
                    data = '-'
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = strutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = strutils.safe_encode(pt.get_string())

    print(result)

def get_instance_list(testscript_file):
    instance_list = []
    headers = [
        'ID',
        'Name',
        'Status',
        'Task State',
        'Power State',
        'Networks'
    ]
    try:
    	with open(testscript_file, 'r') as f:
       	    lines = f.readlines()
            for line in lines:
                discovery_str = line
 
        pop_record = generate_record(discovery_str)
        #print "record is: %s \n" % pop_record
        print '\n========================'
        print '*****INSTANCE LIST******'
        print '========================'
        for pop in pop_record:
            keystone_cred_dict = get_keystone_creds( pop + ".config")
            #print 'keystone creds**********:', keystone_cred_dict
            keystone_cred_dict['pop_name'] = pop 
            record_as_json = json.dumps(keystone_cred_dict)
            #print 'record_as_json#########################:', record_as_json
            configuration = determine_configuration()
            result, content = invoke_remote_test(record_as_json, configuration)
            print '------------'
            print 'POP: %s' % pop
            print '------------'
            print_table(json.loads(content), headers)
            instance_list.append(json.loads(content)) 
            save_instance(content)
        #print 'instance list:***********',instance_list
        return json.dumps(instance_list)
    except IOError as e:
        print e
        return

def main():
    get_instance_list('test_popname.txt')

if __name__ == '__main__':    
    main()
