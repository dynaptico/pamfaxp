#!/usr/bin/env python

import unittest 
import sys
import time
sys.path = ['..:'] + sys.path
from pamfax import PamFax

BASE_URI = 'sandbox-api.pamfax.biz'
USERNAME = 'username'
PASSWORD = 'password'
API_KEY = 'apikey'
API_SECRET = 'apisecret'

# Make sure to add some credit to your sandbox account before running this test.

class TestPamFax(unittest.TestCase):
    """A set of unit tests for this implementation of the PamFax API."""
    
    def test_all(self):
        pamfax = PamFax(USERNAME, PASSWORD, base_uri=BASE_URI, api_key=API_KEY, api_secret=API_SECRET)
        
        # Create a faxjob
        print '*'*10
        print 'Creating a fax job'
        response = pamfax.create()
        print response
        assert response['result']['code'] == 'success'
        faxjob = response
        
        # List available covers
        print '*'*10
        print 'Listing available covers'
        response = pamfax.list_available_covers()
        print response
        assert response['result']['code'] == 'success'
        
        # Add a cover
        print '*'*10
        print 'Adding a cover'
        response = pamfax.set_cover(response['Covers']['content'][1]['id'], 'Dynaptico: Tomorrow On Demand')
        print response
        assert response['result']['code'] == 'success'
        
        # Add a remote file
        print '*'*10
        print 'Adding a remote file'
        response = pamfax.add_remote_file('https://s3.amazonaws.com/dynaptico/Dynaptico.pdf')
        print response
        assert response['result']['code'] == 'success'
        
        # Add a local file
        print '*'*10
        print 'Adding a local file'
        response = pamfax.add_file('Dynaptico.pdf')
        print response
        assert response['result']['code'] == 'success'
        
        # Remove a file
        print '*'*10
        print 'Removing a file'
        response = pamfax.remove_file(response['FaxContainerFile']['file_uuid'])
        print response
        assert response['result']['code'] == 'success'
        
        # Add a recipient
        print '*'*10
        print 'Adding a recipient'
        response = pamfax.add_recipient('+81345789554')
        print response
        assert response['result']['code'] == 'success'
        
        # Add a second recipient
        print '*'*10
        print 'Adding a second recipient'
        response = pamfax.add_recipient('+81362763902')
        print response
        assert response['result']['code'] == 'success'
        
        # Remove a recipient
        print '*'*10
        print 'Removing a recipient'
        response = pamfax.remove_recipient(response['FaxRecipient']['number'])
        print response
        assert response['result']['code'] == 'success'
        
        # List recipients
        print '*'*10
        print 'Listing recipients'
        response = pamfax.list_recipients()
        print response
        assert response['result']['code'] == 'success'
        
        # List fax files
        print '*'*10
        print 'Listing associated fax files'
        response = pamfax.list_fax_files()
        print response
        assert response['result']['code'] == 'success'
        
        # Check state
        print '*'*10
        print 'Checking state'
        t = 0
        while True:
            fax_state = pamfax.get_state()
            print fax_state
            if fax_state['FaxContainer']['state'] == 'ready_to_send':
                break
            time.sleep(2)
            t += 2
            print "%d seconds elapsed..." % t
        assert fax_state['FaxContainer']['state'] == 'ready_to_send'
        
        # Preview fax
        print '*'*10
        print 'Preview the fax'
        response = pamfax.get_preview(faxjob['FaxContainer']['uuid'])
        print response
        assert response['result']['code'] == 'success'
        
        # Send the fax
        print '*'*10
        print 'Send the fax'
        response = pamfax.send()
        print response
        assert response['result']['code'] == 'success'
        
        # Send fax later - only if you don't have enough credit now
        #print '*'*10
        #print 'Send the fax later'
        #response = pamfax.send_later()
        #print response
        #assert response['result']['code'] == 'success'
        
        # Clone the fax
        print '*'*10
        print 'Cloning the fax'
        response = pamfax.clone_fax(faxjob['FaxContainer']['uuid'])
        print response
        assert response['result']['code'] == 'success'
        
if __name__ == '__main__':
    unittest.main()
