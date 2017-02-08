'''
Below code snippet is for getting the list of hosts.
'''

import json
import httplib2
import urllib
import strutils as sutils
import prettytable 
import six
from novaclient.openstack.common import strutils


def generate_record(str):
    '''
    Parse:

    host-list: pop_name=pop2 
    '''
    if str == None:
	print 'Invalid: The test script string should start with \'host-list\'.'
        return 0
    else:
     	#print 'str*********************:',str
       	words = str.split(',')
      	#command = words[0].split()[0]
       	#print(command)
       	#print 'words******************:', words
       	record = {}
       	for w in words:
       	    parts = w.split('=')
            if w.startswith('host-list'):
               	k = parts[0].split()[1].strip()
               	record[k] = parts[1].strip()
            else:
               	record[parts[0].strip()] = parts[1].strip()
    return record

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
        #print 'sa ',  type(sa)
        config[sa[0].strip()] = sa[1].strip()
    #print type(config)
    return config


def invoke_remote_test(record_as_json, configuration):
    '''this function will invoke remote method using REST API'''
    connection = httplib2.Http(".cache")
    headers = { "content-type": "application/x-www-form-urlencoded" }
    #print 'jsonpayload********:', record_as_json
    params = urllib.urlencode({ 'jsonpayload': record_as_json })
    #print 'params:************\n', params
    (response, content) = connection.request(configuration['host_list.url'],
        'GET', headers=headers, body=params)
    #print('Resonse status: reason##### %s: %s' % (response.status, response.reason))
    return response, content


def get_keystone_creds(pop_config_file):
    #print "pop file name: %s \n" % pop_config_file
    d = {}
    with open(pop_config_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            #print 'lines:********\n', line
            line = line.lstrip()
            line = line.rstrip()
            #print 'lstrip(line):********\n', line
            if line.startswith('pop-keystone-access'):
                d['keystone_auth_url'] = line.split('=')[1].lstrip()
            elif line.startswith('OS_USERNAME'):
                d['os_username'] = line.split('=')[1].lstrip()
            elif line.startswith('OS_PASSWORD'):
                d['password'] = line.split('=')[1].lstrip()
            elif line.startswith('OS_TENANT_NAME'):
                d['tenant_id'] = line.split('=')[1].lstrip()
	return d

def get_host_list(testscript_file):
    host_list = []
    headers = [
        'Host Name',
        'Service',
        'zone',
    ]

    try:
        with open(testscript_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                #print 'line***:', line
                if line.startswith('host-list'):
                    test_str = line
                    break
                else:
                    test_str = None

        #print 'test_str:###########', test_str
    except IOError as e:
        print e
        return json.dumps({})
    record = generate_record(test_str)
    print'============================== '
    print'        HOST-LIST              '
    print'============================== '
    if record == 0:
	return
    else:
    	#print "record is: %s \n" % record
    	keystone_cred_dict = get_keystone_creds( record["pop_name"] + ".config")
    	record.update(keystone_cred_dict)
    	#print 'record after update***********:', record
    	record_as_json = json.dumps(record)
    	#print 'record_as_json***********:', record_as_json
    	configuration = determine_configuration()
    	result, content = invoke_remote_test(record_as_json, configuration)
        #print type(content)
        if json.loads(content)["status"]=="ok":
    		#print 'CONTENT#################################:', json.loads(content)["data"]
                print_dict(json.loads(content)["data"], headers)
        else:
		print json.loads(content)["status_msg"] 


def print_dict(objs, fields, formatters={}, sortby_index=None):
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
                #print '$$$$$$$$$$$$o:',o
                #print '$$$$$$$$$$$$filed name:', field_name 
                data = o.get(field_name, '')
                #print '$$$$$$$$$$$$data:', data
                if data is None:
                    data = '-'
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = strutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = strutils.safe_encode(pt.get_string())

    print(result)






def main():
    get_host_list('test_host_list.txt')

if __name__ == '__main__':
    main()
