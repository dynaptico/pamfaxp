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

from httplib import HTTPException
from urllib import urlencode

import mimetypes
import socket
import time

IP_ADDR = socket.gethostbyname(socket.gethostname())

# ----------------------------------------------------------------------------
# "private" helper mehtods
# ----------------------------------------------------------------------------

def _get_and_check_response(http):
    response = http.getresponse()
    codes = (response.status, response.reason)
    print codes
    if response.status != 200:
        raise HTTPException("Response from server not OK: %s %s" % codes)
    return response

def _get(http, url, body=''):
    """Gets the specified url and returns a dict based on the HTTP response in JSON."""
    print "getting url '%s' with body '%s'" % (url, body)
    http.request('GET', url, body, {'Content-Type': 'application/json'})
    response = _get_and_check_response(http)
    return jsonlib.loads(response.read())

def _post(http, url, body, headers={}):
    """Posts to the specified url and returns a dict based on the HTTP response in JSON."""
    print "posting to url '%s' with body '%s'" % (url, body)
    http.request('POST', url, body, headers)
    response = _get_and_check_response(http)
    return jsonlib.loads(response.read())

# ----------------------------------------------------------------------------
# Session
# ----------------------------------------------------------------------------

class Session:
    """
    Class encapsulating a session. Users should not need to
    instantiate this class in applications using PamFax.
    """
    
    def __init__(self, api_credentials, http):
        """
        Instantiates the Session class.
        Note that the api_credentials passed into this method do NOT contain the usertoken field.
        This is different from all other processor classes.
        """
        self.base_url = '/Session'
        self.api_credentials = api_credentials
        self.http = http
    
    def verify_user(self, username, password):
        """
        Calls the VerifyUser url to fetch the verified user details and returns a dict based on the HTTP response in JSON.
        """
        url = '%s/VerifyUser%s&%s' % (self.base_url, self.api_credentials, urlencode({'username': username, 'password': password}))
        return _get(self.http, url)

# ----------------------------------------------------------------------------
# FaxJob
# ----------------------------------------------------------------------------

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
    
    def create(self):
        """Creates a new fax job and returns a dict based on the HTTP response in JSON."""
        url = '%s/Create%s&%s' % (self.base_url, self.api_credentials, urlencode({'user_ip': IP_ADDR, 'user_agent': 'dynaptico-pamfax', 'origin': 'script'}))
        return _get(self.http, url)
    
    def add_recipient(self, number):
        """Adds a recipient to a fax job and returns a dict based on the HTTP response in JSON."""
        url = '%s/AddRecipient%s&%s' % (self.base_url, self.api_credentials, urlencode({'number': number}))
        return _get(self.http, url)
    
    def add_file(self, filename):
        """Adds a local file to the fax job and returns a dict based on the HTTP response in JSON."""
        file = open(filename, 'rb')
        content_type, body = self._encode_multipart_formdata([('filename', filename)], [('file', filename, filename)])
        url = "%s/AddFile%s&%s" % (self.base_url, self.api_credentials, urlencode({'filename': filename}))
        return _post(self.http, url, body, {'Content-Type': content_type, 'Content-Length': str(len(body))})
    
    def add_remote_file(self, url):
        """Adds a remote file to the fax job and returns a dict based on the HTTP response in JSON."""
        url = "%s/AddRemoteFile%s&url=%s" % (self.base_url, self.api_credentials, url)
        return _get(self.http, url)
    
    def cancel(self, uuid):
        """Cancel an outstanding fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/Cancel%s&uuid=%s" % (self.base_url, self.api_credentials, uuid)
        return _get(self.http, url)
    
    def clone_fax(self, uuid):
        """Clone a fax job and returns a dict based on the HTTP response in JSON."""
        url = "%s/CloneFax%s&user_ip=%s&user_agent=dynaptico-pamfax&uuid=%s" % (self.base_url, self.api_credentials, IP_ADDR, uuid)
        return _get(self.http, url)
    
    def list_available_covers(self):
        """Returns the available cover templates as a dict based on the HTTP response in JSON."""
        url = "%s/ListAvailableCovers%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def list_fax_files(self):
        """Returns the files associated to the current faxjob as a dict based on the HTTP response in JSON."""
        url = "%s/ListFaxFiles%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def list_recipients(self):
        """Returns the recipients associated to the current faxjob as a dict based on the HTTP response in JSON."""
        url = "%s/ListRecipients%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def set_cover(self, template_id, text):
        """Sets the current fax cover sheet and returns a dict based on the HTTP response in JSON."""
        url = "%s/SetCover%s&%s" % (self.base_url, self.api_credentials, urlencode({'template_id': template_id, 'text': text}))
        return _get(self.http, url)
    
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
    
    def get_preview(self, uuid):
        """Gets the preview of the pages as a dict based on the HTTP response in JSON."""
        url = "%s/GetPreview%s&uuid=%s" % (self.base_url, self.api_credentials, uuid)
        return _get(self.http, url)
    
    def remove_all_files(self):
        """Remove all of the files associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveAllFiles%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def remove_all_recipients(self):
        """Remove all of the recipients associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveAllRecipients%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def remove_cover(self):
        """Remove all the cover page for the associated fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveCover%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def remove_file(self, file_uuid):
        """Remove a particular file associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveFile%s&%s" % (self.base_url, self.api_credentials, urlencode({'file_uuid': file_uuid}))
        return _get(self.http, url)
    
    def remove_recipient(self, number):
        """Remove a particular recipient associated to a fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/RemoveRecipient%s&%s" % (self.base_url, self.api_credentials, urlencode({'number': number}))
        return _get(self.http, url)
    
    def send(self):
        """Request to send the built fax and returns a dict based on the HTTP response in JSON."""
        url = "%s/Send%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def send_later(self):
        """Request to send the built fax later and returns a dict based on the HTTP response in JSON."""
        url = "%s/SendLater%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def get_fax_state(self):
        """Gets the state of the fax job."""
        url = "%s/GetFaxState%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
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
    
    def _encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------Boundary_of_form_part_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
