"""
This module implements the PamFax API. It has been based heavily off of
Tropo's pamfaxr and tropo-webapi-python projects on GitHub.

See the following link for more details on the PamFax API:

http://www.pamfax.biz/en/extensions/developers/

NOTE: This module has only been tested with python 2.7.
"""

from httplib import HTTPSConnection
from urllib import urlencode

from processors import Common, FaxHistory, FaxJob, NumberInfo, OnlineStorage, Session, Shopping, UserInfo, _get, _get_url

import logging
import sys
import time
import types

logger = logging.getLogger('pamfax')
try:
    logger.addHandler(logging.NullHandler())
except:
    pass
logger.setLevel(logging.DEBUG)

class PamFax:
    """Class encapsulating the PamFax API. Actions related to the sending of faxes are called on objects of this class.
    For example, the 'create' action resides in the FaxJob class, but you can just use the following 'shortcut' logic:
    
    from pamfax import PamFax
    p = PamFax(<args>)
    p.create()
    
    """
    
    def __init__(self, username, password, host='api.pamfax.biz', apikey='', apisecret=''):
        """Creates an instance of the PamFax class and initiates an HTTPS session."""
        logger.info("Connecting to %s", host)
        http = HTTPSConnection(host)
        api_credentials = '?%s' % urlencode({'apikey': apikey, 'apisecret': apisecret, 'apioutputformat': 'API_FORMAT_JSON'})
        usertoken = self._get_user_token(http, api_credentials, username, password)
        api_credentials = '%s&%s' % (api_credentials, urlencode({'usertoken': usertoken}))
        common = Common(api_credentials, http)
        fax_history = FaxHistory(api_credentials, http)
        fax_job = FaxJob(api_credentials, http)
        number_info = NumberInfo(api_credentials, http)
        online_storage = OnlineStorage(api_credentials, http)
        session = Session(api_credentials, http)
        shopping = Shopping(api_credentials, http)
        user_info = UserInfo(api_credentials, http)
        attrs = dir(self)
        for processor in (session, common, fax_history, fax_job, number_info, online_storage, shopping, user_info):
            for attr_key in dir(processor):
                if attr_key not in attrs:
                    attr_value = getattr(processor, attr_key)
                    if isinstance(attr_value, types.MethodType):
                        setattr(self, attr_key, attr_value)
    
    def _verify_user(self, http, api_credentials, username, password):
        """Verifies a user via username/password"""
        url = _get_url('/Session', 'VerifyUser', api_credentials, username=username, password=password)
        return _get(http, url)
    
    def _get_user_token(self, http, api_credentials, username, password):
        """Gets the user token to use with subsequent requests."""
        result = self._verify_user(http, api_credentials, username, password)
        if result['result']['code'] == 'success':
            return result['UserToken']['token']
        else:
            raise Exception(result['result']['message'])
    
    # ------------------------------------------------------------------------
    # Convenient helper methods
    # ------------------------------------------------------------------------
    
    def get_state(self, blocking=False, interval=1):
        """Obtains the state of the FaxJob build, may block until a state is received, or just return immediately"""
        if blocking:
            state = None
            result = None
            while state is None:
                result = self.get_fax_state()
                time.sleep(interval)
            return result
        else:
            return self.get_fax_state()
    
    def is_converting(self, fax_state):
        """Returns whether or not a file in the fax job is still in a converting state."""
        converting = False
        files = fax_state['Files']
        if 'content' in files:
            for f in files['content']:
                state = f['state']
                if state == '' or state == 'converting':
                    converting = True
        return converting

if __name__ == '__main__':
    print >>sys.stderr, """

 This is the Python implementation of the PamFax API.

 To run the test suite, please run:

    cd test
    python test.py

"""
