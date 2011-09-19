"""
This module implements the PamFax API. It has been based heavily off of
Tropo's pamfaxr and tropo-webapi-python projects on GitHub.

See the following link for more details on the PamFax API:

http://www.pamfax.biz/en/extensions/developers/

NOTE: This module has only been tested with python 2.7.
"""

try:
    import cjson as jsonlib
    jsonlib.dumps = jsonlib.encode
    jsonlib.loads = jsonlib.decode
except ImportError:
    try:
        from django.utils import simplejson as jsonlib
    except ImportError:
        try:
            import simplejson as jsonlib
        except ImportError:
            import json as jsonlib

from httplib import HTTPSConnection
from urllib import urlencode

import multipart
import socket
import time
import types

IP_ADDR = socket.gethostbyname(socket.gethostname())

class ValidationError(Exception):
    """Subclass of Exception that indicates a failure to validate with the PamFax API."""
    pass

class FaxJob:
    """
    Class encapsulating a specific fax job. Users should not need to
    instantiate this class in applications using PamFax.
    """
    
    def __init__(self, api_credentials, http):
        """Instantiates the FaxJob class"""
        self.base_url = '/FaxJob'
        self.api_credentials = api_credentials
        self.http = http
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     },
    #     "FaxContainer": {
    #         "price": 0,
    #         "send_mail": 0,
    #         "uuid": "ebKVV4XGwx99Wu",
    #         "error_notification": 0,
    #         "group_notification": 0,
    #         "send_sms": 0,
    #         "currency_rate": 1,
    #         "cover_page_length": nil,
    #         "send_chat": 0,
    #         "pages": nil,
    #         "cover_id": 0,
    #         "currency": true,
    #         "affiliatepartner": nil,
    #         "updated": nil,
    #         "cover_text": nil,
    #         "processing_started": nil,
    #         "created": "2011-01-17 19:27:57",
    #         "state": "editing"
    #     }
    # }
    def create(self):
        """Creates a new fax job and returns a dict based on the HTTP response in JSON."""
        url = '%s/Create%s&%s' % (self.base_url, self.api_credentials, urlencode({'user_ip': IP_ADDR, 'user_agent': 'pamfax.py', 'origin': 'script'}))
        return self._get(url)
    
    #   pamfax.add_recipient('14155551212')
    #
    #   returns:
    #
    #   {
    #           "result": {
    #            "code": "success",
    #           "count": 1,
    #         "message": ""
    #     },
    #     "FaxRecipient": {
    #         "price_per_page": 0.09,
    #                   "name": "",
    #                 "number": "+14155551212",
    #           "price_source": "PNR",
    #                "country": "US",
    #              "area_code": "415",
    #                   "zone": "1",
    #            "number_type": "FIXED",
    #            "description": "California (CA)"
    #     }
    #   }
    def add_recipient(self, number):
        """Adds a recipient to a fax job and returns a dict based on the HTTP response in JSON."""
        url = '%s/AddRecipient%s&%s' % (self.base_url, self.api_credentials, urlencode({'number': number}))
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     },
    #     "FaxContainerFile": {
    #         "name": "/path_to_my_file/filename.pdf",
    #         "file_order": 1,
    #         "ext": "pdf",
    #         "file_uuid": "JNMi19AeQ6QkoC",
    #         "mime": "application/pdf",
    #         "state": ""
    #     }
    # }
    def add_file(self, filename):
        """Adds a local file to the fax job and returns a dict based on the HTTP response in JSON."""
        file = open(filename, 'rb')
        content_type, body = multipart.encode_multipart_formdata([('filename', filename)], [('file', filename, filename)])
        url = "%s/AddFile%s&%s" % (self.base_url, self.api_credentials, urlencode({'filename': filename}))
        return self._post(url, body, {'Content-Type': content_type, 'Content-Length': str(len(body))})
        
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     },
    #     "FaxContainerFile": {
    #         "name": "Tropo.pdf",
    #         "file_order": 0,
    #         "ext": "pdf",
    #         "file_uuid": "CwPx31xjl9k7Cp",
    #         "mime": "application/pdf",
    #         "state": ""
    #     }
    # }
    def add_remote_file(self, url):
        """Adds a remote file to the fax job and returns a dict based on the HTTP response in JSON."""
        url = "%s/AddRemoteFile%s&url=%s" % (self.base_url, self.api_credentials, url)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def cancel(self, uuid):
        """Cancel an outstanding fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/Cancel%s&uuid=%s" % (self.base_url, self.api_credentials, uuid)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "fax_not_found",
    #         "count": 0,
    #         "message": "Fax not found"
    #     }
    # }
    def clone_fax(self, uuid):
        """Clone a fax job and returns a dict based on the HTTP response in JSON."""
        url = "%s/CloneFax%s&user_ip=%s&user_agent=pamfax.py&uuid=%s" % (self.base_url, self.api_credentials, IP_ADDR, uuid)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     },
    #     "Covers": {
    #         "type": "list",
    #         "content": [
    #             [0] {
    #                 "template_id": "eae27d77ca20db309e056e3d2dcd7d69",
    #                       "title": "Basic",
    #                     "creator": 0,
    #                          "id": 1,
    #                    "thumb_id": "091d584fced301b442654dd8c23b3fc9",
    #                 "description": nil,
    #                  "preview_id": "7eabe3a1649ffa2b3ff8c02ebfd5659f"
    #             },
    #             [1] {
    #                 "template_id": "ca46c1b9512a7a8315fa3c5a946e8265",
    #                       "title": "Flowers",
    #                     "creator": 0,
    #                          "id": 3,
    #                    "thumb_id": "45fbc6d3e05ebd93369ce542e8f2322d",
    #                 "description": nil,
    #                  "preview_id": "979d472a84804b9f647bc185a877a8b5"
    #             },
    #             [2] {
    #                 "template_id": "e96ed478dab8595a7dbda4cbcbee168f",
    #                       "title": "Message",
    #                     "creator": 0,
    #                          "id": 4,
    #                    "thumb_id": "ec8ce6abb3e952a85b8551ba726a1227",
    #                 "description": nil,
    #                  "preview_id": "63dc7ed1010d3c3b8269faf0ba7491d4"
    #             },
    #             [3] {
    #                 "template_id": "f340f1b1f65b6df5b5e3f94d95b11daf",
    #                       "title": "Simple",
    #                     "creator": 0,
    #                          "id": 5,
    #                    "thumb_id": "335f5352088d7d9bf74191e006d8e24c",
    #                 "description": nil,
    #                  "preview_id": "cb70ab375662576bd1ac5aaf16b3fca4"
    #             }
    #         ]
    #     }
    # }
    def list_available_covers(self):
        """Returns the available cover templates as a dict based on the HTTP response in JSON."""
        url = "%s/ListAvailableCovers%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     },
    #     "Files": {
    #         "type": "list",
    #         "content": [
    #             [0] {
    #                 "name": "Tropo.pdf",
    #                 "size": 646768,
    #                 "extension": "pdf",
    #                 "uuid": "CwPx31xjl9k7Cp",
    #                 "pages": 101,
    #                 "contentmd5": "fd898b168b9780212a2ddd5bfbd79d65",
    #                 "mimetype": "application/pdf",
    #                 "created": "2011-01-17 19:28:05"
    #             }
    #         ]
    #     }
    # }
    def list_fax_files(self):
        """Returns the files associated to the current faxjob as a dict based on the HTTP response in JSON."""
        url = "%s/ListFaxFiles%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     },
    #     "Recipients": {
    #         "type": "list",
    #         "content": [
    #             {
    #                               "price": 0,
    #                            "duration": 0,
    #                                "name": "",
    #                    "delivery_started": nil,
    #                      "price_per_page": 0.09,
    #                              "number": "+13035551212",
    #                        "price_source": "PNR",
    #                             "country": "US",
    #                                "sent": nil,
    #                           "completed": nil,
    #                           "area_code": "303",
    #                    "formatted_number": "+1 303 5551212",
    #                                "zone": "1",
    #                                "uuid": "ExozS0NJe7CErm",
    #                       "currency_rate": "1",
    #                               "pages": nil,
    #                         "status_code": 0,
    #                         "number_type": "FIXED",
    #                 "transmission_report": "",
    #                            "currency": "1",
    #                         "description": "Colorado (CO)",
    #                             "updated": "2011-01-17 19:28:16",
    #                      "status_message": nil,
    #                             "created": "2011-01-17 19:28:16",
    #                               "state": "unknown"
    #             },
    #                 {
    #                               "price": 0,
    #                            "duration": 0,
    #                                "name": "",
    #                    "delivery_started": nil,
    #                      "price_per_page": 0.09,
    #                              "number": "+14155551212",
    #                        "price_source": "PNR",
    #                             "country": "US",
    #                                "sent": nil,
    #                           "completed": nil,
    #                           "area_code": "415",
    #                    "formatted_number": "+1 415 5551212",
    #                                "zone": "1",
    #                                "uuid": "yoAT88QXAda80g",
    #                       "currency_rate": "1",
    #                               "pages": nil,
    #                         "status_code": 0,
    #                         "number_type": "FIXED",
    #                 "transmission_report": "",
    #                            "currency": "1",
    #                         "description": "California (CA)",
    #                             "updated": "2011-01-17 19:28:14",
    #                      "status_message": nil,
    #                             "created": "2011-01-17 19:28:14",
    #                               "state": "unknown"
    #             }
    #         ]
    #     }
    # }
    def list_recipients(self):
        """Returns the recipients associated to the current faxjob as a dict based on the HTTP response in JSON."""
        url = "%s/ListRecipients%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def set_cover(self, template_id, text):
        """Sets the current fax cover sheet and returns a dict based on the HTTP response in JSON."""
        url = "%s/SetCover%s&%s" % (self.base_url, self.api_credentials, urlencode({'template_id': template_id, 'text': text}))
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 2,
    #         "message": ""
    #     },
    #     "converting": false,
    #         "Files": {
    #         "type": "list",
    #             "content": [
    #                 [0] {
    #                     "file_order": 0,
    #                     "state": "converted"
    #                 }
    #             ]
    #         },
    #         "FaxContainer": {
    #             "price": 18.36,
    #             "sms_cost": 0,
    #             "send_mail": "0",
    #             "uuid": "ebKVV4XGwx99Wu",
    #             "error_notification": "0",
    #             "group_notification": "0",
    #             "send_sms": "0",
    #             "currency_rate": 1,
    #             "cover_page_length": "1",
    #             "send_chat": "0",
    #             "pages": 102,
    #             "cover_id": 3,
    #             "currency": true,
    #             "affiliatepartner": nil,
    #             "updated": "2011-01-17 19:28:22",
    #             "cover_text": "Foobar is here!",
    #             "processing_started": nil,
    #             "created": "2011-01-17 19:27:57",
    #             "state": "ready_to_send"
    #     }
    # }
    def get_state(self, blocking=False, interval=1):
        """Obtains the state of the FaxJob build, may block until a stateis received, or just return immediately"""
        if blocking:
            state = None
            result = None
            while state is None:
                result = self.get_fax_state()
                time.sleep(interval)
            return result
        else:
            return self.get_fax_state()
    
    # {
    #     "Status": {
    #         "open": 5,
    #         "done": 0
    #     },
    #     "result": {
    #         "code": "success",
    #         "count": 2,
    #         "message": ""
    #     },
    #     "PreviewPages": {
    #         "type": "list"
    #     }
    # }
    def get_preview(self, uuid):
        """Gets the preview of the pages as a dict based on the HTTP response in JSON."""
        url = "%s/GetPreview%s&uuid=%s" % (self.base_url, self.api_credentials, uuid)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def remove_all_files(self):
        """Remove all of the files associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveAllFiles%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def remove_all_recipients(self):
        """Remove all of the recipients associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveAllRecipients%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def remove_cover(self):
        """Remove all the cover page for the associated fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveCover%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def remove_file(self, file_uuid):
        """Remove a particular file associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveFile%s&%s" % (self.base_url, self.api_credentials, urlencode({'file_uuid': file_uuid}))
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 1,
    #         "message": ""
    #     }
    # }
    def remove_recipient(self, number):
        """Remove a particular recipient associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveRecipient%s&%s" % (self.base_url, self.api_credentials, urlencode({'number': number}))
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "not_enough_credit",
    #         "count": 0,
    #         "message": "You don't have enough PamFax Credit. <a href=\\\"https://www.pamfax.biz/shop\\\">Buy PamFax Credit now</a>."
    #     }
    # }
    def send(self):
        """Request to send the built fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/Send%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    # {
    #     "result": {
    #         "code": "success",
    #         "count": 0,
    #         "message": ""
    #     }
    # }
    def send_later(self):
        """Request to send the built fax later and returns a dict based on the HTTP response in JSON."""
        url = "%s/SendLater%s" % (self.base_url, self.api_credentials)
        return self._get(url)
    
    def get_fax_state(self):
        """Gets the state of the fax job."""
        url = "%s/GetFaxState%s" % (self.base_url, self.api_credentials)
        self.http.request('GET', url)
        response = self.http.getresponse()
        fax_state = jsonlib.loads(response.read())
        fax_state['converting'] = self.is_converting(fax_state)
        return fax_state
    
    def is_converting(self, fax_state):
        """Returns whether or not a file in the fax job is still in a converting state."""
        converting = False
        files = fax_state['Files']
        if 'content' in files:
            for file in files['content']:
                state = file['state']
                if state == '' or state == 'converting':
                    converting = True
        return converting
    
    def _get(self, url, body=''):
        """Gets the specified url and returns a dict based on the HTTP response in JSON."""
        print "getting url '%s' with body '%s'" % (url, body)
        self.http.request('GET', url, body, {'Content-Type': 'application/json'})
        response = self.http.getresponse()
        print response.status, response.reason
        return jsonlib.loads(response.read())
    
    def _post(self, url, body, headers={}):
        """Posts to the specified url and returns a dict based on the HTTP response in JSON."""
        print "posting to url '%s' with body '%s'" % (url, body)
        self.http.request('POST', url, body, headers)
        response = self.http.getresponse()
        print response.status, response.reason
        return jsonlib.loads(response.read())

class PamFax:
    """
    Class encapsulating the PamFax API. Actions related to the sending of faxes are called on objects of this class.
    """
    
    def __init__(self, username, password, base_uri='api.pamfax.biz', api_key='', api_secret=''):
        """Creates an instance of the PamFax class"""
        self.http = HTTPSConnection(base_uri)
        api_credentials = '?%s' % urlencode({'apikey': api_key, 'apisecret': api_secret, 'apioutputformat': 'API_FORMAT_JSON'})
        user_token = self.get_user_token(api_credentials, username, password)
        api_credentials = '%s&%s' % (api_credentials, urlencode({'usertoken': user_token}))
        faxjob = FaxJob(api_credentials, self.http)
        attrs = dir(self)
        for attr_key in dir(faxjob):
            if attr_key not in attrs:
                attr_value = getattr(faxjob, attr_key)
                if isinstance(attr_value, types.MethodType):
                    setattr(self, attr_key, attr_value)
        self.faxjob = faxjob
    
    def get_user_token(self, api_credentials, username, password):
        """Gets the user token to use with subsequent requests."""
        result = self.verify_user(api_credentials, username, password)
        if result['result']['code'] == 'success':
            return result['UserToken']['token']
        else:
            raise ValidationError(result['result']['message'])
    
    def verify_user(self, api_credentials, username, password):
        """Calls the VerifyUser url to fetch the verified user details and returns a dict based on the HTTP response in JSON."""
        url = '/Session/VerifyUser%s&%s' % (api_credentials, urlencode({'username': username, 'password': password}))
        print "getting url %s" % url
        self.http.request('GET', url)
        response = self.http.getresponse()
        body = response.read()
        print response.status, response.reason, body
        return jsonlib.loads(body)

if __name__ == '__main__':
    print """

 This is the Python implementation of the PamFax API.

 To run the test suite, please run:

    cd test
    python test.py

"""
