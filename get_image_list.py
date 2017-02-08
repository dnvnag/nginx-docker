'''
Below code snippet is for getting the image list from the server.
'''

import json
import httplib2
import urllib
#from novaclient import utils
import strutils as sutils
import prettytable 
def generate_record( str):
    '''
    Parse:
    provision pop_name = pop1, pop2 
    '''
    #print 'str*********************:',str
    str = str.strip()
    words = str.split('=')
    #command = words[0].split()[0]
    #print('command')
    #print(command)
    #print 'words******************:', words
    record = {}
    parts = words[1].split(',')
    for i in xrange(len(parts)):
        parts[i] = parts[i].strip()    
    #print 'parts***********************:', parts
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
    (response, content) = connection.request(configuration['image.url'],
        'GET', headers=headers, body=params)
    #print('Resonse status: reason##### %s: %s' % (response.status, response.reason))
    return response, content

def save_instance(content):
    file_name = 'image.info'
    with open(file_name, 'a+') as f:
        f.write(content+' ') 
        f.write('\n')	

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

def get_image_list(testscript_file):
    image_list = []
    try:
        with open(testscript_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                discovery_str = line
    except IOError as e:
        print e
        return json.dumps({})
    pop_record = generate_record(discovery_str)
    #print "record is: %s \n" % pop_record
    print '\n======================'
    print '******IMAGE LIST******'
    print '======================'
    for pop in pop_record:
        keystone_cred_dict = get_keystone_creds( pop + ".config")
        keystone_cred_dict['pop_name'] = pop 
        record_as_json = json.dumps(keystone_cred_dict)
        #print 'record_as_json***********:', record_as_json
        configuration = determine_configuration()
        result, content = invoke_remote_test(record_as_json, configuration)
        #print 'CONTENT#################################:', json.loads(content)
        print '------------'
        print 'POP: %s' % pop
        print '------------'
        if json.loads(content).get('status')=='error':
		print json.loads(content).get('status_msg')
        else:
 
                print_table(json.loads(content).get('data'), ['ID', 'Name', 'Status', 'Server'])
        #image_list.append(json.loads(content)) 
        save_instance(content)
    #print 'Image list:***********',image_list
    return json.dumps(image_list)

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
                data = o.get(field_name, '')
                if data is None:
                    data = '-'
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = sutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = sutils.safe_encode(pt.get_string())

    print(result)

def main():
    get_image_list('test_popname.txt')

if __name__ == '__main__':
    main()
