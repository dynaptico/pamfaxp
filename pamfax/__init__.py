"""
This module implements the PamFax API. It has been based heavily off of
Tropo's pamfaxr and tropo-webapi-python projects on GitHub.

See the following link for more details on the PamFax API:

http://www.pamfax.biz/en/extensions/developers/

NOTE: This module has only been tested with python 2.7.
"""

from httplib import HTTPSConnection
from urllib import urlencode

from processors import Common, FaxHistory, FaxJob, NumberInfo, OnlineStorage, Session, Shopping, UserInfo

import types

class PamFax:
    """
    Class encapsulating the PamFax API. Actions related to the sending of faxes are called on objects of this class.
    For example, the 'create' action resides in the FaxJob class, but you can just use the following 'shortcut' logic:
    
    from pamfax import PamFax
    p = PamFax(<args>)
    p.create()
    """
    
    def __init__(self, username, password, base_uri='api.pamfax.biz', api_key='', api_secret=''):
        """Creates an instance of the PamFax class and initiates an HTTPS session."""
        api_credentials = '?%s' % urlencode({'apikey': api_key, 
                                             'apisecret': api_secret, 
                                             'apioutputformat': 'API_FORMAT_JSON'})
        print "Connecting to %s" % base_uri
        http = HTTPSConnection(base_uri)
        session = Session(api_credentials, http)
        user_token = self.get_user_token(session, username, password)
        api_credentials = '%s&%s' % (api_credentials, urlencode({'usertoken': user_token}))
        common = Common(api_credentials, http)
        fax_history = FaxHistory(api_credentials, http)
        fax_job = FaxJob(api_credentials, http)
        number_info = NumberInfo(api_credentials, http)
        online_storage = OnlineStorage(api_credentials, http)
        shopping = Shopping(api_credentials, http)
        user_info = UserInfo(api_credentials, http)
        attrs = dir(self)
        for processor in (session, common, fax_history, fax_job, number_info, online_storage, shopping, user_info):
            for attr_key in dir(processor):
                if attr_key not in attrs:
                    attr_value = getattr(processor, attr_key)
                    if isinstance(attr_value, types.MethodType):
                        setattr(self, attr_key, attr_value)
    
    def get_user_token(self, session, username, password):
        """Gets the user token to use with subsequent requests."""
        result = session.verify_user(username, password)
        if result['result']['code'] == 'success':
            return result['UserToken']['token']
        else:
            raise Exception(result['result']['message'])

if __name__ == '__main__':
    print """

 This is the Python implementation of the PamFax API.

 To run the test suite, please run:

    cd test
    python test.py

"""
