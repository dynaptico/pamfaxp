"""
The classes defined in this module should correspond 1-to-1 to the 
specifications in the PamFax API docs. See the link below for more info:

    https://sandbox-apifrontend.pamfax.biz/summary/processors/

Users should not need to instantiate this class in applications using PamFax.
Instead, just call the action directly on the PamFax object, and it will be
delegated to the correct processor automatically.
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

from httplib import HTTPException
from urllib import urlencode

import mimetypes
import socket
import time

IP_ADDR = socket.gethostbyname(socket.gethostname())
CONTENT_TYPE = 'content-type'
CONTENT_TYPE_JSON = 'application/json'

# ----------------------------------------------------------------------------
# "private" helper mehtods
# ----------------------------------------------------------------------------

def _get_and_check_response(http):
    """
    Wait for the HTTP response and throw an exception if the return 
    status is not OK.
    """
    response = http.getresponse()
    codes = (response.status, response.reason)
    print codes, response.getheaders()
    if response.status != 200:
        raise HTTPException("Response from server not OK: %s %s" % codes)
    return response

def _get(http, url, body=''):
    """
    Gets the specified url and returns either a dict based on the 
    HTTP response in JSON, or if the response is not in JSON format,
    return a tuple containing the data in the body and the content type.
    """
    print "getting url '%s' with body '%s'" % (url, body)
    http.request('GET', url, body, {'Content-Type': CONTENT_TYPE_JSON})
    response = _get_and_check_response(http)
    content_type = response.getheader(CONTENT_TYPE, None)
    if content_type is not None and content_type.startswith(CONTENT_TYPE_JSON):
        return jsonlib.loads(response.read())
    else:
        return (response.read(), content_type)

def _post(http, url, body, headers={}):
    """
    Posts to the specified url and returns either a dict based on the 
    HTTP response in JSON, or if the response is not in JSON format,
    return a tuple containing the data in the body and the content type.
    """
    print "posting to url '%s' with body '%s'" % (url, body)
    http.request('POST', url, body, headers)
    response = _get_and_check_response(http)
    content_type = response.getheader(CONTENT_TYPE, None)
    if content_type is not None and content_type.startswith(CONTENT_TYPE_JSON):
        return jsonlib.loads(response.read())
    else:
        return (response.read(), content_type)

# ----------------------------------------------------------------------------
# Common
# ----------------------------------------------------------------------------

class Common:
    """Class encapsulating common actions for the PamFax API"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the Common class"""
        self.base_url = '/Common'
        self.api_credentials = api_credentials
        self.http = http
    
    def get_current_settings(self):
        pass
    
    def get_file(self, file_uuid):
        """Gets a file with the given file_uuid and returns both its binary data and headers that give the filename and mimetype."""
        url = '%s/GetFile%s&%s' % (self.base_url, self.api_credentials, urlencode({'file_uuid': file_uuid}))
        return _get(self.http, url)
    
    def get_geo_ip_information(self):
        pass
    
    def get_page_preview(self):
        pass
    
    def list_constants(self):
        pass
    
    def list_countries(self):
        pass
    
    def list_countries_for_zone(self):
        pass
    
    def list_currencies(self):
        pass
    
    def list_languages(self):
        pass
    
    def list_strings(self):
        pass
    
    def list_supported_file_types(self):
        pass
    
    def list_timezones(self):
        pass
    
    def list_versions(self):
        pass
    
    def list_zones(self):
        pass

# ----------------------------------------------------------------------------
# FaxHistory
# ----------------------------------------------------------------------------

class FaxHistory:
    """Class encapsulating actions related to fax history for this account"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the FaxHistory class"""
        self.base_url = '/FaxHistory'
        self.api_credentials = api_credentials
        self.http = http
    
    def add_fax_note(self, fax_uuid, note):
        """Adds a note to an item in the fax history and returns a dict based on the HTTP response in JSON."""
        url = '%s/AddFaxNote%s&%s' % (self.base_url, self.api_credentials, urlencode({'fax_uuid': fax_uuid, 'note': note}))
        return _get(self.http, url)
    
    def count_faxes(self):
        pass
    
    def delete_fax(self):
        pass
    
    def delete_fax_from_trash(self):
        pass
    
    def delete_faxes(self):
        pass
    
    def delete_faxes_from_trash(self):
        pass
    
    def empty_trash(self):
        pass
    
    def get_fax_details(self):
        pass
    
    def get_fax_group(self):
        pass
    
    def get_inbox_fax(self):
        pass
    
    def get_transmission_report(self):
        pass
    
    def list_fax_group(self):
        pass
    
    def list_fax_notes(self):
        pass
    
    def list_inbox_faxes(self, current_page=1, items_per_page=20):
        """Lists all faxes in the inbox of the current user and returns a dict based on the HTTP response in JSON."""
        url = '%s/ListInboxFaxes%s&%s' % (self.base_url, self.api_credentials, urlencode({'current_page': current_page, 
                                                                                          'items_per_page': items_per_page}))
        return _get(self.http, url)
    
    def list_outbox_faxes(self):
        pass
    
    def list_recent_faxes(self):
        pass
    
    def list_sent_faxes(self):
        pass
    
    def list_trash(self):
        pass
    
    def list_unpaid_faxes(self):
        pass
    
    def restore_fax(self):
        pass
    
    def set_fax_read(self):
        pass
    
    def set_faxes_as_read(self):
        pass
    
    def set_spam_state_for_faxes(self):
        pass
    

# ----------------------------------------------------------------------------
# FaxJob
# ----------------------------------------------------------------------------

class FaxJob:
    """Class encapsulating a specific fax job"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the FaxJob class"""
        self.base_url = '/FaxJob'
        self.api_credentials = api_credentials
        self.http = http
    
    def add_file(self, filename):
        """Adds a local file to the fax job and returns a dict based on the HTTP response in JSON."""
        file = open(filename, 'rb')
        content_type, body = self._encode_multipart_formdata([('filename', filename)], [('file', filename, filename)])
        url = "%s/AddFile%s&%s" % (self.base_url, self.api_credentials, urlencode({'filename': filename}))
        return _post(self.http, url, body, {'Content-Type': content_type, 'Content-Length': str(len(body))})
    
    def add_file_from_online_storage(self, filename):
        pass
    
    def add_recipient(self, number):
        """Adds a recipient to a fax job and returns a dict based on the HTTP response in JSON."""
        url = '%s/AddRecipient%s&%s' % (self.base_url, self.api_credentials, urlencode({'number': number}))
        return _get(self.http, url)
    
    def add_recipients(self, number):
        pass
    
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
    
    def create(self):
        """Creates a new fax job and returns a dict based on the HTTP response in JSON."""
        url = '%s/Create%s&%s' % (self.base_url, self.api_credentials, urlencode({'user_ip': IP_ADDR, 'user_agent': 'dynaptico-pamfax', 'origin': 'script'}))
        return _get(self.http, url)
    
    def get_fax_state(self):
        """Gets the state of the fax job."""
        url = "%s/GetFaxState%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def get_preview(self, uuid):
        """Gets the preview of the pages as a dict based on the HTTP response in JSON."""
        url = "%s/GetPreview%s&uuid=%s" % (self.base_url, self.api_credentials, uuid)
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
    
    def send_delayed_fax_now(self):
        pass
    
    def send_later(self):
        """Request to send the built fax later and returns a dict based on the HTTP response in JSON."""
        url = "%s/SendLater%s" % (self.base_url, self.api_credentials)
        return _get(self.http, url)
    
    def send_unpaid(self):
        pass
    
    def send_unpaid_faxes(self):
        pass
    
    def set_cover(self, template_id, text):
        """Sets the current fax cover sheet and returns a dict based on the HTTP response in JSON."""
        url = "%s/SetCover%s&%s" % (self.base_url, self.api_credentials, urlencode({'template_id': template_id, 'text': text}))
        return _get(self.http, url)
    
    def set_notifications(self):
        pass
    
    def set_recipients(self):
        pass
    
    def start_preview_creation(self):
        pass
    
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

# ----------------------------------------------------------------------------
# NumberInfo
# ----------------------------------------------------------------------------

class NumberInfo:
    """Class encapsulating information for a given fax number"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the NumberInfo class"""
        self.base_url = '/NumberInfo'
        self.api_credentials = api_credentials
        self.http = http
    
    def get_number_info(self):
        pass
    
    def get_page_price(self):
        pass

# ----------------------------------------------------------------------------
# OnlineStorage
# ----------------------------------------------------------------------------

class OnlineStorage:
    """Class encapsulating actions related to online storage"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the OnlineStorage class"""
        self.base_url = '/OnlineStorage'
        self.api_credentials = api_credentials
        self.http = http
    
    def authenticate(self):
        pass
    
    def drop_authentication(self):
        pass
    
    def get_provider_logo(self):
        pass
    
    def list_folder_contents(self):
        pass
    
    def list_providers(self):
        pass
    
    def set_auth_token(self):
        pass

# ----------------------------------------------------------------------------
# Session
# ----------------------------------------------------------------------------

class Session:
    """Class encapsulating a PamFax session"""
    
    def __init__(self, api_credentials, http):
        """
        Instantiates the Session class.
        Note that the api_credentials passed into this method do NOT contain the usertoken field.
        This is different from all other processor classes.
        """
        self.base_url = '/Session'
        self.api_credentials = api_credentials
        self.http = http
    
    def create_login_identifier(self):
        pass
    
    def list_changes(self):
        pass
    
    def logout(self):
        pass
    
    def ping(self):
        pass
    
    def register_listener(self):
        pass
    
    def reload_user(self):
        pass
    
    def verify_user(self, username, password):
        """
        Calls the VerifyUser url to fetch the verified user details and returns a dict based on the HTTP response in JSON.
        """
        url = '%s/VerifyUser%s&%s' % (self.base_url, self.api_credentials, urlencode({'username': username, 'password': password}))
        return _get(self.http, url)

# ----------------------------------------------------------------------------
# Shopping
# ----------------------------------------------------------------------------

class Shopping:
    """Class encapsulating shopping options available through PamFax"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the Shopping class"""
        self.base_url = '/Shopping'
        self.api_credentials = api_credentials
        self.http = http
    
    def add_credit_to_sandbox_user(self):
        pass
    
    def get_invoice(self):
        pass
    
    def get_nearest_fax_in_number(self):
        pass
    
    def get_shop_link(self):
        pass
    
    def list_available_items(self):
        pass
    
    def list_fax_in_areacodes(self):
        pass
    
    def list_fax_in_countries(self):
        pass
    
    def redeem_credit_voucher(self):
        pass

# ----------------------------------------------------------------------------
# UserInfo
# ----------------------------------------------------------------------------

class UserInfo:
    """Class encapsulating user info"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the UserInfo class"""
        self.base_url = '/UserInfo'
        self.api_credentials = api_credentials
        self.http = http
    
    def create_user(self):
        pass
    
    def delete_user(self):
        pass
    
    def get_culture_info(self):
        pass
    
    def get_users_avatar(self):
        pass
    
    def has_avatar(self):
        pass
    
    def has_plan(self):
        pass
    
    def list_expirations(self):
        pass
    
    def list_inboxes(self):
        pass
    
    def list_orders(self):
        pass
    
    def list_profiles(self):
        pass
    
    def list_user_agents(self):
        pass
    
    def list_wall_messages(self):
        pass
    
    def save_user(self):
        pass
    
    def send_message(self):
        pass
    
    def send_password_reset_message(self):
        pass
    
    def set_online_storage_settings(self):
        pass
    
    def set_password(self):
        pass
    
    def set_profile_properties(self):
        pass
    
    def validate_new_username(self):
        pass
