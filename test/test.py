#!/usr/bin/env python

from pamfax import PamFax

import socket
import sys
import unittest
import time

sys.path = ['..:'] + sys.path

IP_ADDR = socket.gethostbyname('www.dynaptico.com')

BASE_URI = 'sandbox-api.pamfax.biz'
USERNAME = 'username'
PASSWORD = 'password'
API_KEY = 'apikey'
API_SECRET = 'apisecret'

# Make sure to add some credit to your sandbox account before running this test.

def _assert(message, response):
    print message
    print response
    assert response['result']['code'] == 'success'
    print '*'*10

class TestPamFax(unittest.TestCase):
    """A set of unit tests for this implementation of the PamFax API."""
    
    def test_Common(self):
        pamfax = PamFax(USERNAME, PASSWORD, base_uri=BASE_URI, api_key=API_KEY, api_secret=API_SECRET)
        
        message = 'Getting current settings'
        response = pamfax.get_current_settings()
        _assert(message, response)
        
        #message = 'Getting file'
        #response = pamfax.get_file(file_uuid)
        #_assert(message, response)
        
        message = 'Getting geo IP information'
        response = pamfax.get_geo_ip_information(IP_ADDR)
        _assert(message, response)
        
        #message = 'Getting page preview'
        #response = pamfax.get_page_preview(uuid, page_no)
        #_assert(message, response)
        
        message = 'Listing countries'
        response = pamfax.list_countries()
        _assert(message, response)
        
        message = 'Listing countries for zone'
        response = pamfax.list_countries_for_zone(1)
        _assert(message, response)
        
        message = 'Listing currencies 1'
        response = pamfax.list_currencies()
        _assert(message, response)
        
        message = 'Listing currencies 2'
        response = pamfax.list_currencies('JPY')
        _assert(message, response)
        
        message = 'Listing languages 1'
        response = pamfax.list_languages()
        _assert(message, response)
        
        message = 'Listing languages 2'
        response = pamfax.list_languages(50)
        _assert(message, response)
        
        #message = 'Listing strings'
        #response = pamfax.list_strings(['string1', 'string2'])
        #_assert(message, response)
        
        message = 'Listing supported file types'
        response = pamfax.list_supported_file_types()
        _assert(message, response)
        
        message = 'Listing timezones'
        response = pamfax.list_timezones()
        _assert(message, response)
        
        message = 'Listing versions'
        response = pamfax.list_versions()
        _assert(message, response)
        
        message = 'Listing zones'
        response = pamfax.list_zones()
        _assert(message, response)
    
#    def test_FaxHistory(self):
#        pamfax = PamFax(USERNAME, PASSWORD, base_uri=BASE_URI, api_key=API_KEY, api_secret=API_SECRET)
#        
#        message = 'Adding note to fax'
#        response = pamfax.add_fax_note(fax_uuid, note)
#        _assert(message, response)
#        
#        message = 'Counting faxes'
#        response = pamfax.count_faxes()
#        _assert(message, response)
#        
#        message = 'Deleting fax'
#        response = pamfax.delete_fax()
#        _assert(message, response)
#        
#        message = 'Deleting fax from trash'
#        response = pamfax.delete_fax_from_trash()
#        _assert(message, response)
#        
#        message = 'Deleting faxes'
#        response = pamfax.delete_faxes()
#        _assert(message, response)
#        
#        message = 'Deleting faxes from trash'
#        response = pamfax.delete_faxes_from_trash()
#        _assert(message, response)
#        
#        message = 'Emptying trash'
#        response = pamfax.empty_trash()
#        _assert(message, response)
#        
#        message = 'Getting fax details'
#        response = pamfax.get_fax_details()
#        _assert(message, response)
#        
#        message = 'Getting fax group'
#        response = pamfax.get_fax_group()
#        _assert(message, response)
#        
#        message = 'Getting inbox fax'
#        response = pamfax.get_inbox_fax()
#        _assert(message, response)
#        
#        message = 'Getting transmission report'
#        response = pamfax.get_transmission_report()
#        _assert(message, response)
#        
#        message = 'Listing fax group'
#        response = pamfax.list_fax_group()
#        _assert(message, response)
#        
#        message = 'Listing fax notes'
#        response = pamfax.list_fax_notes()
#        _assert(message, response)
#        
#        message = 'Listing inbox faxes'
#        response = pamfax.list_inbox_faxes()
#        _assert(message, response)
#        
#        message = 'Listing outbox faxes'
#        response = pamfax.list_outbox_faxes()
#        _assert(message, response)
#        
#        message = 'Listing recent faxes'
#        response = pamfax.list_recent_faxes()
#        _assert(message, response)
#        
#        message = 'Listing sent faxes'
#        response = pamfax.list_sent_faxes()
#        _assert(message, response)
#        
#        message = 'Listing trash'
#        response = pamfax.list_trash()
#        _assert(message, response)
#        
#        message = 'Listing unpaid faxes'
#        response = pamfax.list_unpaid_faxes()
#        _assert(message, response)
#        
#        message = 'Restoring fax'
#        response = pamfax.restore_fax()
#        _assert(message, response)
#        
#        message = 'Setting fax as read'
#        response = pamfax.set_fax_read()
#        _assert(message, response)
#        
#        message = 'Setting faxes as read'
#        response = pamfax.set_faxes_as_read()
#        _assert(message, response)
#        
#        message = 'Setting spam state for faxes'
#        response = pamfax.set_spam_state_for_faxes()
#        _assert(message, response)
    
    def test_FaxJob(self):
        pamfax = PamFax(USERNAME, PASSWORD, base_uri=BASE_URI, api_key=API_KEY, api_secret=API_SECRET)
        
        message = 'Creating a fax job'
        response = pamfax.create()
        _assert(message, response)
        
        message = 'Listing available covers'
        response = pamfax.list_available_covers()
        _assert(message, response)
        
        message = 'Adding a cover'
        response = pamfax.set_cover(response['Covers']['content'][1]['id'], 'Dynaptico: Tomorrow On Demand')
        _assert(message, response)
        
        message = 'Adding a remote file'
        response = pamfax.add_remote_file('https://s3.amazonaws.com/dynaptico/Dynaptico.pdf')
        _assert(message, response)
        
        message = 'Adding a local file'
        response = pamfax.add_file('Dynaptico.pdf')
        _assert(message, response)
        
        message = 'Removing a file'
        response = pamfax.remove_file(response['FaxContainerFile']['file_uuid'])
        _assert(message, response)
        
        message = 'Adding recipient 1'
        response = pamfax.add_recipient('+81345789554')
        _assert(message, response)
        
        message = 'Adding recipient 2'
        response = pamfax.add_recipient('+81362763902')
        _assert(message, response)
        
        message = 'Removing a recipient'
        response = pamfax.remove_recipient(response['FaxRecipient']['number'])
        _assert(message, response)
        
        message ='Listing recipients'
        response = pamfax.list_recipients()
        _assert(message, response)
        
        message = 'Listing fax files'
        response = pamfax.list_fax_files()
        _assert(message, response)
        
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
        
        message = 'Preview the fax'
        response = pamfax.get_preview()
        _assert(message, response)
        
        message = 'Send the fax'
        response = pamfax.send()
        _assert(message, response)
        
        # This only works if you don't have enough credit now
        #message = 'Send the fax later'
        #response = pamfax.send_later()
        #_assert(message, response)
        
        # This only works after the fax has moved to the fax history
        #message = 'Cloning the fax'
        #response = pamfax.clone_fax(faxjob['FaxContainer']['uuid'])
        #_assert(message, response)
    
    def test_NumberInfo(self):
        pamfax = PamFax(USERNAME, PASSWORD, base_uri=BASE_URI, api_key=API_KEY, api_secret=API_SECRET)
        
        message = 'Getting number info'
        response = pamfax.get_number_info('+81362763902')
        _assert(message, response)
        
        message = 'Getting page price'
        response = pamfax.get_page_price('+81362763902')
        _assert(message, response)

if __name__ == '__main__':
    unittest.main()
