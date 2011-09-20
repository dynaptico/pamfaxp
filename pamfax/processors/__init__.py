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
USER_AGENT = 'dynaptico-pamfax'
ORIGIN = 'script'
CONTENT_TYPE = 'content-type'
CONTENT_TYPE_JSON = 'application/json'

# ----------------------------------------------------------------------------
# "private" helper mehtods
# ----------------------------------------------------------------------------

def _get_url(base_url, action, api_credentials, **kwargs):
    """Construct the URL that corresponds to a given action.
    All kwargs whose value is None are filtered out
    """
    url = '%s/%s%s' % (base_url, action, api_credentials)
    if len(kwargs) == 0:
        return url
    query = {}
    for arg in kwargs:
        if kwargs[arg] is not None:
            query[arg] = kwargs[arg]
    url = '%s&%s' % (url, urlencode(query))
    return url

def _get_and_check_response(http):
    """
    Wait for the HTTP response and throw an exception if the return 
    status is not OK. Return either a dict based on the 
    HTTP response in JSON, or if the response is not in JSON format,
    return a tuple containing the data in the body and the content type.
    """
    response = http.getresponse()
    codes = (response.status, response.reason)
    print codes
    if response.status != 200:
        raise HTTPException("Response from server not OK: %s %s" % codes)
    content_type = response.getheader(CONTENT_TYPE, None)
    if content_type is not None and content_type.startswith(CONTENT_TYPE_JSON):
        return jsonlib.loads(response.read())
    else:
        return (response.read(), content_type)

def _get(http, url, body=''):
    """Gets the specified url and returns the response."""
    print "getting url '%s' with body '%s'" % (url, body)
    http.request('GET', url, body)
    return _get_and_check_response(http)

def _post(http, url, body, headers={}):
    """Posts to the specified url and returns the response."""
    print "posting to url '%s' with body '%s'" % (url, body)
    http.request('POST', url, body, headers)
    return _get_and_check_response(http)

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
        """Returns the current settings for timezone and currency.
        This is the format/timezone ALL return values of the API are in. These are taken from the user
        (if logged in, the api user's settings or the current ip address)
        """
        url = _get_url(self.base_url, 'GetCurrentSettings', self.api_credentials)
        return _get(self.http, url)
    
    def get_file(self, file_uuid):
        """Returns file content.
        Will return binary data and headers that give the filename and mimetype.
        Note: User identified by usertoken must be owner of the file or
        the owner must have shared this file to the requesting user.
        Share dependencies are resolved (dependend on the type) via the
        fax_inbox, fax_history_files or user_covers table.
        """
        url = _get_url(self.base_url, 'GetFile', self.api_credentials, file_uuid=file_uuid)
        return _get(self.http, url)
    
    def get_geo_ip_information(self, ip):
        """Returns Geo information based on the given IP address (IPV4)"""
        url = _get_url(self.base_url, 'GetGeoIPInformation', self.api_credentials, ip=ip)
        return _get(self.http, url)
    
    def get_page_preview(self, uuid, page_no, max_width=None, max_height=None):
        """Returns a preview page for a fax.
        May be in progress, sent or from inbox.
        """
        url = _get_url(self.base_url, 'GetPagePreview', self.api_credentials, uuid=uuid, page_no=page_no, max_width=max_width, max_height=max_height)
        return _get(self.http, url)
    
    def list_constants(self):
        """DEPRECATED"""
        return None
    
    def list_countries(self):
        """Returns all countries with their translated names and the default zone"""
        url = _get_url(self.base_url, 'ListCountries', self.api_credentials)
        return _get(self.http, url)
    
    def list_countries_for_zone(self, zone):
        """Returns all countries in the given zone
        Result includes their translated names, countrycode and country-prefix.
        """
        url = _get_url(self.base_url, 'ListCountriesForZone', self.api_credentials, zone=zone)
        return _get(self.http, url)
    
    def list_currencies(self, code=None):
        """Returns the list of supported currencies.
        Result contains convertion rates too.
        If code is given will only return the specified currency's information.
        """
        url = _get_url(self.base_url, 'ListCurrencies', self.api_credentials, code=code)
        return _get(self.http, url)
    
    def list_languages(self, min_percent_translated=None):
        """List all available languages.
        Result may be filtered tso that only languages are returned that are
        at least translated $min_percent_translated %
        """
        url = _get_url(self.base_url, 'ListLanguages', self.api_credentials, min_percent_translated=min_percent_translated)
        return _get(self.http, url)
    
    def list_strings(self, ids, culture=None):
        """Returns a list of strings translated into the given language."""
        url = _get_url(self.base_url, 'ListStrings', self.api_credentials, ids=ids, culture=culture)
        return _get(self.http, url)
    
    def list_supported_file_types(self):
        """Returns the supported file types for documents that can be faxed."""
        url = _get_url(self.base_url, 'ListSupportedFileTypes', self.api_credentials)
        return _get(self.http, url)
    
    def list_timezones(self):
        """List all supported timezones"""
        url = _get_url(self.base_url, 'ListTimezones', self.api_credentials)
        return _get(self.http, url)
    
    def list_versions(self):
        """Lists the current Versions.
        Result contains versions for the PamFax Gadget, Client etc and returns
        the version and update url
        """
        url = _get_url(self.base_url, 'ListVersions', self.api_credentials)
        return _get(self.http, url)
    
    def list_zones(self):
        """Returns price and price_pro for a given zone"""
        url = _get_url(self.base_url, 'ListZones', self.api_credentials)
        return _get(self.http, url)

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
        """Add a note (free text) to the fax"""
        url = _get_url(self.base_url, 'AddFaxNote', self.api_credentials, fax_uuid=fax_uuid, note=note)
        return _get(self.http, url)
    
    def count_faxes(self, type):
        """
        Returns the number of faxes from users history with a specific state.
        Possible values: history, inbox, inbox_unread, outbox or unpaid
        """
        url = _get_url(self.base_url, 'CountFaxes', self.api_credentials, type=type)
        return _get(self.http, url)
    
    def delete_fax(self):
        """DEPRECATED! Use DeleteFaxes instead"""
        return None
    
    def delete_fax_from_trash(self):
        """DEPRECATED! Use DeleteFaxesFromTrash instead"""
        return None
    
    def delete_faxes(self, uuids, siblings_too=None):
        """
        Moves faxes to the trash.
        If siblings_too is true will perform for the given faxes and all other recipients
        from the same fax jobs.
        siblings_too will only be evaluated for uuids beloging to an outgoing fax and will be
        ignored for incoming faxes uuids
        """
        url = _get_url(self.base_url, 'DeleteFaxes', self.api_credentials, uuids=uuids, siblings_too=siblings_too)
        return _get(self.http, url)
    
    def delete_faxes_from_trash(self, uuids):
        """
        Removes faxes from trash
        This method is similar to EmptyTrash() which deletes all the faxes from trash
        """
        url = _get_url(self.base_url, 'DeleteFaxesFromTrash', self.api_credentials, uuids=uuids)
        return _get(self.http, url)
    
    def empty_trash(self):
        """
        Removes all faxes from trash for user and if user is member of a
        company and has delete rights also for the owners inbox faxes
        """
        url = _get_url(self.base_url, 'EmptyTrash', self.api_credentials)
        return _get(self.http, url)
    
    def get_fax_details(self, uuid):
        """Returns the details of a fax in progress."""
        url = _get_url(self.base_url, 'GetFaxDetails', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def get_fax_group(self, uuid):
        """Returns a fax groups details."""
        url = _get_url(self.base_url, 'GetFaxGroup', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def get_inbox_fax(self, uuid, mark_read=None):
        """Returns the details of a fax in the inbox."""
        url = _get_url(self.base_url, 'GetInboxFax', self.api_credentials, uuid=uuid, mark_read=mark_read)
        return _get(self.http, url)
    
    def get_transmission_report(self, uuid):
        """
        Get a .pdf-Version of a transmission report.
        On the transmission report basic data of the fax and a preview of the first page is shown.
        Should always be called with API_MODE_PASSTHRU, as the result is the pdf as binary data
        """
        url = _get_url(self.base_url, 'GetTransmissionReport', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def list_fax_group(self, uuid, current_page=None, items_per_page=None):
        """Lists all faxes in a group (that are sent as on job)."""
        url = _get_url(self.base_url, 'ListFaxGroup', self.api_credentials, uuid=uuid, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_fax_notes(self, fax_uuid):
        """Lists all notes for the given fax in reverse order (latest first)"""
        url = _get_url(self.base_url, 'ListFaxNotes', self.api_credentials, fax_uuid=fax_uuid)
        return _get(self.http, url)
    
    def list_inbox_faxes(self, current_page=None, items_per_page=None):
        """List all faxes in the inbox of the current user."""
        url = _get_url(self.base_url, 'ListInboxFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_outbox_faxes(self, current_page=None, items_per_page=None):
        """Faxes in the outbox that are currently in the sending process"""
        url = _get_url(self.base_url, 'ListOutboxFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_recent_faxes(self, count=None, data_to_list=None):
        """
        Returns a list of latest faxes for the user.
        Does not contain deleted and delayed faxes (See ListTrash for deleted faxes).
        """
        url = _get_url(self.base_url, 'ListRecentFaxes', self.api_credentials, count=count, data_to_list=data_to_list)
        return _get(self.http, url)
    
    def list_sent_faxes(self, current_page=None, items_per_page=None):
        """List all sent faxes (successful or not)"""
        url = _get_url(self.base_url, 'ListSentFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_trash(self, current_page=None, items_per_page=None):
        """List all faxes in trash"""
        url = _get_url(self.base_url, 'ListTrash', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_unpaid_faxes(self, current_page=None, items_per_page=None):
        """
        Lists all unpaid faxes that are waiting for a payment.
        When this user makes a transaction to add credit, these faxes will be sent automatically
        if they are younger that 2 hours.
        """
        url = _get_url(self.base_url, 'ListUnpaidFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def restore_fax(self, uuid):
        """Restores a fax from the trash."""
        url = _get_url(self.base_url, 'RestoreFax', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def set_fax_read(self, uuid):
        """
        Sets a fax' read date to current time.
        Fax needs to be a fax in the inbox.
        """
        url = _get_url(self.base_url, 'SetFaxRead', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def set_faxes_as_read(self, uuids):
        """Sets the read date of all the faxes to the current time"""
        url = _get_url(self.base_url, 'SetFaxesAsRead', self.api_credentials, uuids=uuids)
        return _get(self.http, url)
    
    def set_spam_state_for_faxes(self, uuids, is_spam=None):
        """
        Sets the spamscore for all the faxes depending on the flag "is_spam"
        Takes an array of faxes UUIDs and marks them a spam if the second argument (is_spam) is true.
        Removes the Spam state if is_spam is false.
        If 15 or more faxes of the same sender has been marked as spam, all incoming faxes are directly moved to the trash.
        This is user specific, so if user A reports 15 faxes of one sender, then only all incoming faxes from the sender to
        him are directly sent to the trash.
        """
        url = _get_url(self.base_url, 'SetSpamStateForFaxes', self.api_credentials, uuids=uuids, is_spam=is_spam)
        return _get(self.http, url)

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
    
    def add_file(self, filename, origin=None):
        """Adds a file to the current fax.
        Requires the file to be uploaded as POST paramter named 'file' as a standard HTTP upload. This could be either Content-type: multipart/form-data with file content as base64-encoded data or as Content-type: application/octet-stream with just the binary data.
        See http://www.faqs.org/rfcs/rfc1867.html for documentation on file uploads.
        """
        file = open(filename, 'rb')
        content_type, body = self._encode_multipart_formdata([('filename', filename)], [('file', filename, filename)])
        url = _get_url(self.base_url, 'AddFile', self.api_credentials, filename=filename, origin=origin)
        return _post(self.http, url, body, {'Content-Type': content_type, 'Content-Length': str(len(body))})
    
    def add_file_from_online_storage(self, provider, uuid):
        """Add a file identified by an online storage identifier.
        You'll have to use the OnlineStorageApi to identify a user for an online storage provider first
        and then get listings of his files. These will contain the file identifiers used by this method.
        """
        url = _get_url(self.base_url, 'AddFileFromOnlineStorage', self.api_credentials, provider=provider, uuid=uuid)
        return _get(self.http, url)
    
    def add_recipient(self, number, name=None):
        """Adds a recipient to the current fax."""
        url = _get_url(self.base_url, 'AddRecipient', self.api_credentials, number=number, name=name)
        return _get(self.http, url)
    
    def add_recipients(self, numbers, names=None):
        """Adds recipients to the current fax.
        The given recipients will be added to current recipients.
        """
        url = _get_url(self.base_url, 'AddRecipients', self.api_credentials, numbers=numbers, names=names)
        return _get(self.http, url)
    
    def add_remote_file(self, url):
        """Add a remote file to the fax.
        url may contain username:password for basic http auth, but this is the only supported
        authentication method.
        URL Examples:
        http://myusername:andpassord
        """
        url = _get_url(self.base_url, 'AddRemoteFile', self.api_credentials, url=url)
        return _get(self.http, url)
    
    def cancel(self, uuid, siblings_too=None):
        """Cancels fax sending for a fax recipient or a whole fax job.
        If siblings_too is true will cancel all faxes in the job the
        fax with uuid belongs to.
        """
        url = _get_url(self.base_url, 'Cancel', self.api_credentials, uuid=uuid, siblings_too=siblings_too)
        return _get(self.http, url)
    
    def clone_fax(self, uuid, user_ip=IP_ADDR, user_agent=USER_AGENT):
        """Clones an already sent fax in the API backend and returns it."""
        url = _get_url(self.base_url, 'CloneFax', self.api_credentials, uuid=uuid, user_ip=user_ip, user_agent=user_agent)
        return _get(self.http, url)
    
    def create(self, user_ip=IP_ADDR, user_agent=USER_AGENT, origin=ORIGIN):
        """Creates a new fax in the API backend and returns it.
        If a fax job is currently in edit mode in this session, this fax job is returned instead.
        Note: This is not an error. It provides you with the possibility to continue with the fax.
        """
        url = _get_url(self.base_url, 'Create', self.api_credentials, user_ip=user_ip, user_agent=user_agent, origin=origin)
        return _get(self.http, url)
    
    def get_fax_state(self):
        """Returns the state of the current fax."""
        url = _get_url(self.base_url, 'GetFaxState', self.api_credentials)
        return _get(self.http, url)
    
    def get_preview(self):
        """Returns the states of all preview pages."""
        url = _get_url(self.base_url, 'GetPreview', self.api_credentials)
        return _get(self.http, url)
    
    def list_available_covers(self):
        """Returns a list of all coverpages the user may use.
        Result includes the "no cover" if the fax job already contains a file as in that case
        there's no need to add a cover.
        """
        url = _get_url(self.base_url, 'ListAvailableCovers', self.api_credentials)
        return _get(self.http, url)
    
    def list_fax_files(self):
        """Get all uploaded files for the current fax"""
        url = _get_url(self.base_url, 'ListFaxFiles', self.api_credentials)
        return _get(self.http, url)
    
    def list_recipients(self, current_page=None, items_per_page=None):
        """Returns the recipients for the current fax."""
        url = _get_url(self.base_url, 'ListRecipients', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def remove_all_files(self):
        """Remove all uploaded files from the current fax"""
        url = _get_url(self.base_url, 'RemoveAllFiles', self.api_credentials)
        return _get(self.http, url)
    
    def remove_all_recipients(self):
        """Removes all recipients for the current fax."""
        url = _get_url(self.base_url, 'RemoveAllRecipients', self.api_credentials)
        return _get(self.http, url)
    
    def remove_cover(self):
        """Removes the cover from fax"""
        url = _get_url(self.base_url, 'RemoveCover', self.api_credentials)
        return _get(self.http, url)
    
    def remove_file(self, file_uuid):
        """Remove a file from the current fax."""
        url = _get_url(self.base_url, 'RemoveFile', self.api_credentials, file_uuid=file_uuid)
        return _get(self.http, url)
    
    def remove_recipient(self, number):
        """Removes a recipient from the current fax"""
        url = _get_url(self.base_url, 'RemoveRecipient', self.api_credentials, number=number)
        return _get(self.http, url)
    
    def send(self, send_at=None):
        """Start the fax sending.
        Only successfull if all necessary data is set to the fax: at least 1 recipient and a cover page or a file uploaded.
        Will only work if user has enough credit to pay for the fax.
        You may pass in a datetime when the fax shall be sent. This must be a string formatted in the users chosen culture
        (so exactly as you would show it to him) and may not be in the past nor be greater than 'now + 14days'.
        """
        url = _get_url(self.base_url, 'Send', self.api_credentials, send_at=send_at)
        return _get(self.http, url)
    
    def send_delayed_fax_now(self, uuid):
        """Send a previously delayed fax now.
        Use this method if you want to send a fax right now that was initially delayed (by giving a send_at value into Send).
        """
        url = _get_url(self.base_url, 'SendDelayedFaxNow', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def send_later(self, send_at=None):
        """Put the fax in the unpaid faxes queue.
        Only possible if user has NOT enough credit to send this fax directly.
        You may pass in a datetime when the fax shall be sent. This must be a string formatted in the users chosen culture
        (so exactly as you would show it to him) and may not be in the past nor be greater than 'now + 14days'.
        """
        url = _get_url(self.base_url, 'SendLater', self.api_credentials, send_at=send_at)
        return _get(self.http, url)
    
    def send_unpaid(self):
        """DEPRECATED! Use SendUnpaidFaxes instead"""
        return None
    
    def send_unpaid_faxes(self, uuids):
        """Send unpaid faxes
        Will work until credit reaches zero.
        Will return two lists: SentFaxes and UnpaidFaxes that contain the
        faxes that could or not be sent.
        """
        url = _get_url(self.base_url, 'SendUnpaidFaxes', self.api_credentials, uuids=uuids)
        return _get(self.http, url)
    
    def set_cover(self, template_id, text=None):
        """Sets the cover template for the current fax."""
        url = _get_url(self.base_url, 'SetCover', self.api_credentials, template_id=template_id, text=text)
        return _get(self.http, url)
    
    def set_notifications(self, notifications, group_notification=None, error_notification=None, save_defaults=None):
        """Sets the notification options for the current fax.
        Notification options that are not in the array will not be changed/resetted.
        Note: defaults for notification settings will be taken from users account, so potentially not need
        to call this on every fax.
        """
        url = _get_url(self.base_url, 'SetNotifications', self.api_credentials, notifications=notifications, group_notification=group_notification, error_notification=error_notification, save_defaults=save_defaults)
        return _get(self.http, url)
    
    def set_recipients(self, numbers, names=None):
        """Creates recipients for the current fax.
        All recipients are replaced with the given ones!
        """
        url = _get_url(self.base_url, 'SetRecipients', self.api_credentials, numbers=numbers, names=names)
        return _get(self.http, url)
    
    def start_preview_creation(self):
        """Starts creating the preview for this fax.
        Call after fax is ready (GetFaxState returns FAX_READY_TO_SEND)
        """
        url = _get_url(self.base_url, 'StartPreviewCreation', self.api_credentials)
        return _get(self.http, url)
    
    # ------------------------------------------------------------------------
    # Special helper methods
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
    
    def get_number_info(self, faxnumber):
        """Get some information about a fax number.
        Result contains zone, type, city, ...
        Validates and corrects the number too.
        """
        url = _get_url(self.base_url, 'GetNumberInfo', self.api_credentials, faxnumber=faxnumber)
        return _get(self.http, url)
    
    def get_page_price(self, faxnumber):
        """Calculate the expected price per page to a given fax number.
        Use GetNumberInfo when you do not need pricing information, as calculating expected price takes longer then just looking up the info for a number.
        """
        url = _get_url(self.base_url, 'GetPagePrice', self.api_credentials, faxnumber=faxnumber)
        return _get(self.http, url)

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
    
    def authenticate(self, provider, username, password):
        """Authenticate the current user for a Provider.
        This is a one-time process and must be done only once for each user.
        PamFax API will perform the login and store only an authentication token which
        will be enaugh for future use of the service.
        """
        url = _get_url(self.base_url, 'Authenticate', self.api_credentials, provider=provider, username=username, password=password)
        return _get(self.http, url)
    
    def drop_authentication(self, provider):
        """Will drop the users authentication for the given provider.
        This will permanently erase all data related to the account!
        """
        url = _get_url(self.base_url, 'DropAuthentication', self.api_credentials, provider=provider)
        return _get(self.http, url)
    
    def get_provider_logo(self, provider, size):
        """Outputs a providers logo in a given size.
        Call ListProviders for valid sizes per Provider.
        """
        url = _get_url(self.base_url, 'GetProviderLogo', self.api_credentials, provider=provider, size=size)
        return _get(self.http, url)
    
    def list_folder_contents(self, provider, folder=None, clear_cache=None):
        """Lists all files and folders inside a given folder.
        Leave folder empty to get the contents of the root folder.
        User must be autheticated for the provider given here to be able to recieve listings (see Authenticate method).
        If clear_cache is set to true all subitems will be deleted and must be refetched (previously cached UUIDs are invalid)
        """
        url = _get_url(self.base_url, 'ListFolderContents', self.api_credentials, provider=provider, folder=folder, clear_cache=clear_cache)
        return _get(self.http, url)
    
    def list_providers(self, attach_settings=None):
        """Returns a list of supported providers."""
        url = _get_url(self.base_url, 'ListProviders', self.api_credentials, attach_settings=attach_settings)
        return _get(self.http, url)
    
    def set_auth_token(self, provider, token, username=None):
        """Manually sets auth token for the current user.
        token must contain an associative array including the tokens.
        sample (google):
        'auth_token_cp'=>DQAAAHoAAADCrkpB7Ip_vuelbla2UKE9s_ObVKTNA_kT6Ej26SwddJvMUmEz_9qbLlZJnsAdm583Sddp_0FYS9QmmwoUpf51RHxkgPUL20OqsdAP5OnCgY_TdVbvXX8tMQBBX30V4_NhTcE_0sI6zhba5Y3yZWV5nljliG98eA36ybekKucuhQ
        'auth_token_writely'=>DQAAAHoAAADCrkpB7Ip_vuelbla2UKE9s_ObVKTNA_kT6Ej62SDwdJvMUmEz_9qbLlZJnsAdm583Sddp_0FYS9QmmwoUpf51RHxkgPUL20OqsdAP5OnCgY_TdVbvXX8tMQBBX30V4_NhTcE_0sI6zhba5Y3yZWV5nljliG98eA36ybekKucuhQ
        'auth_token_wise'=>DQAAAHoAAADCrkpB7Ip_vuelbla2UKE9s_ObVKTNA_kT6Ej26SDdwJvMUmEz_9qbLlZJnsAdm583Sddp_0FYS9QmmwoUpf51RHxkgPUL20OqsdAP5OnCgY_TdVbvXX8tMQBBX30V4_NhTcE_0sI6zhba5Y3yZWV5nljliG98eA36ybekKucuhQ
        'auth_token_lh2'=>DQAAAHoAAADCrkpB7Ip_vuelbla2UKE9s_ObkvTNA_kT6Ej26SDwdJvMUmEz_9qbLlZJnsAdm583Sddp_0FYS9QmmwoUpf51RHxkgPUL20OqsdAP5OnCgY_TdVbvXX8tMQBBX30V4_NhTcE_0sI6zhba5Y3yZWV5nljliG98eA36ybekKucuhQ
        """
        url = _get_url(self.base_url, 'SetAuthToken', self.api_credentials, provider=provider, token=token, username=username)
        return _get(self.http, url)

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
    
    def create_login_identifier(self, user_ip=None, timetolifeminutes=None):
        """Creates an identifier for the current user, which then can be passed to the portal to directly log in the user: https://portal.pamfax.biz/?_id=
        Be aware that these identifiers are case sensitive. Identifiers with ttl > 0 can only be used once.
        """
        url = _get_url(self.base_url, 'CreateLoginIdentifier', self.api_credentials, user_ip=user_ip, timetolifeminutes=timetolifeminutes)
        return _get(self.http, url)
    
    def list_changes(self):
        """Returns all changes in the system that affect the currently logged in user. This could be changes to the user's profile, credit, settings, ...
        Changes will be deleted after you received them once via this call, so use it wisely ;)
        """
        url = _get_url(self.base_url, 'ListChanges', self.api_credentials)
        return _get(self.http, url)
    
    def logout(self):
        """Terminate the current session. Log out."""
        url = _get_url(self.base_url, 'Logout', self.api_credentials)
        return _get(self.http, url)
    
    def ping(self):
        """Just keeps a session alive. If there is no activity in a Session for 5 minutes, it will be terminated.
        You then would need to call Session::VerifyUser again and start a new FaxJob
        """
        url = _get_url(self.base_url, 'Ping', self.api_credentials)
        return _get(self.http, url)
    
    def register_listener(self, listener_types, append=None):
        """Registers listeners for the current session. Any change of the listened types will then be available via Session::ListChanges function"""
        url = _get_url(self.base_url, 'RegisterListener', self.api_credentials, listener_types=listener_types, append=append)
        return _get(self.http, url)
    
    def reload_user(self):
        """Returns the current user object.
        Use this if you need to ensure that your locally stored user
        object is up to date.
        """
        url = _get_url(self.base_url, 'ReloadUser', self.api_credentials)
        return _get(self.http, url)
    
    def verify_user(self, username, password):
        """Verifies a user via username/password"""
        url = _get_url(self.base_url, 'VerifyUser', self.api_credentials, username=username, password=password)
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
    
    def add_credit_to_sandbox_user(self, amount, reason=None):
        """Adds some credit in user's currency to the currently logged in user.
        NOTES:
        This method is for testing purposes only, so it is not available in the LIVE system. Use it to create
        some 'virtual' credits for your users.
        """
        url = _get_url(self.base_url, 'AddCreditToSandboxUser', self.api_credentials, amount=amount, reason=reason)
        return _get(self.http, url)
    
    def get_invoice(self, payment_uuid, hidecopy=None):
        """Returns an invoice pdf file for a payment (see UserInfo/ListOrders).
        Returns binary data so call with API_FORMAT_PASSTHRU.
        """
        url = _get_url(self.base_url, 'GetInvoice', self.api_credentials, payment_uuid=payment_uuid, hidecopy=hidecopy)
        return _get(self.http, url)
    
    def get_nearest_fax_in_number(self, ip_address):
        """Get the nearest available fax-in area code for the given IP-Address.
        Used to show "You can get a fax-in number in ..." to the user to offer PamFax plans to him
        """
        url = _get_url(self.base_url, 'GetNearestFaxInNumber', self.api_credentials, ip_address=ip_address)
        return _get(self.http, url)
    
    def get_shop_link(self, type=None, product=None, pay=None):
        """Returns different shop links.
        Use these links to open a browser window with the shop in a specific state.
        """
        url = _get_url(self.base_url, 'GetShopLink', self.api_credentials, type=type, product=product, pay=pay)
        return _get(self.http, url)
    
    def list_available_items(self):
        """Returns a list of available items from the shop.
        When a user is logged in, it will also contain the items only available to validated customers.
        """
        url = _get_url(self.base_url, 'ListAvailableItems', self.api_credentials)
        return _get(self.http, url)
    
    def list_fax_in_areacodes(self, country_code, state=None):
        """Returns available fax-in area codes in a given country+state"""
        url = _get_url(self.base_url, 'ListFaxInAreacodes', self.api_credentials, country_code=country_code, state=state)
        return _get(self.http, url)
    
    def list_fax_in_countries(self):
        """Retruns a list of countries where new fax-in numbers are currently available"""
        url = _get_url(self.base_url, 'ListFaxInCountries', self.api_credentials)
        return _get(self.http, url)
    
    def redeem_credit_voucher(self, vouchercode):
        """Redeem a credit voucher.
        These are different then the shop vouchers to be used in the online shop!
        You can use "PCPC0815" to test this function in the Sandbox API
        """
        url = _get_url(self.base_url, 'RedeemCreditVoucher', self.api_credentials, vouchercode=vouchercode)
        return _get(self.http, url)

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
    
    def create_user(self, name, username, password, email, culture, externalprofile=None, campaign_id=None):
        """Create a new PamFax user and logs him in"""
        url = _get_url(self.base_url, 'CreateUser', self.api_credentials, name=name, username=username, password=password, email=email, culture=culture, externalprofile=externalprofile, campaign_id=campaign_id)
        return _get(self.http, url)
    
    def delete_user(self):
        """Deletes the currently logged in users account.
        All assigned numbers and data will be deleted too!
        Warning: User will be deleted permanently without any chance to recover his data!
        """
        url = _get_url(self.base_url, 'DeleteUser', self.api_credentials)
        return _get(self.http, url)
    
    def get_culture_info(self):
        """Returns the users culture information"""
        url = _get_url(self.base_url, 'GetCultureInfo', self.api_credentials)
        return _get(self.http, url)
    
    def get_users_avatar(self, provider=None):
        """Returns avatars for current user"""
        url = _get_url(self.base_url, 'GetUsersAvatar', self.api_credentials, provider=provider)
        return _get(self.http, url)
    
    def has_avatar(self):
        """Return if Avatar is available or not"""
        url = _get_url(self.base_url, 'HasAvator', self.api_credentials)
        return _get(self.http, url)
    
    def has_plan(self):
        """Check if the user has a Plan.
        This would NOT include other fax numbers user has access to. Will return NONE if no plan, PRO or BASIC otherwise
        """
        url = _get_url(self.base_url, 'HasPlan', self.api_credentials)
        return _get(self.http, url)
    
    def list_expirations(self, type=None):
        """Returns expirations from current user
        if type==false all Expirations are Returned
        else CREDIT, PROPLAN and
        """
        url = _get_url(self.base_url, 'ListExpirations', self.api_credentials, type=type)
        return _get(self.http, url)
    
    def list_inboxes(self, expired_too=None, shared_too=None):
        """Return the inboxes of the user with some additional data (like expiration)."""
        url = _get_url(self.base_url, 'ListInboxes', self.api_credentials, expired_too=expired_too, shared_too=shared_too)
        return _get(self.http, url)
    
    def list_orders(self, current_page=None, items_per_page=None):
        """Returns a list of orders for this user"""
        url = _get_url(self.base_url, 'ListOrders', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_profiles(self):
        """Read the full profile of the user."""
        url = _get_url(self.base_url, 'ListProfiles', self.api_credentials)
        return _get(self.http, url)
    
    def list_user_agents(self, max=None):
        """Returns a list of user-agents the user has used to sent faxes.
        List will be sorted by amount of faxes sent, so it is a top max list.
        """
        url = _get_url(self.base_url, 'ListUserAgents', self.api_credentials, max=max)
        return _get(self.http, url)
    
    def list_wall_messages(self, count=None, data_to_list=None):
        """Returns a list of activities for the user
        This list contains report about what has been happened lately in users account
        (like messages sent to the user, faxes sent, faxes received, orders placed, ...)
        """
        url = _get_url(self.base_url, 'ListWallMessages', self.api_credentials, count=count, data_to_list=data_to_list)
        return _get(self.http, url)
    
    def save_user(self, user=None, profile=None):
        """Saves user profile"""
        url = _get_url(self.base_url, 'SaveUser', self.api_credentials, user=user, profile=profile)
        return _get(self.http, url)
    
    def send_message(self, body, type=None, recipient=None, subject=None):
        """Send a message to the user"""
        url = _get_url(self.base_url, 'SendMessage', self.api_credentials, body=body, type=type, recipient=recipient, subject=subject)
        return _get(self.http, url)
    
    def send_password_reset_message(self, username, user_ip=None):
        """Send a password reset message to a user"""
        url = _get_url(self.base_url, 'SendPasswordResetMessage', self.api_credentials, username=username, user_ip=user_ip)
        return _get(self.http, url)
    
    def set_online_storage_settings(self, provider, settings):
        """Sets users OnlineStorage settings.
        Expects the settings to be given as key-value pairs.
        Currently supported settings are:
        - inbox_enabled: Store incoming faxes (0|1, required)
        - inbox_path: Path to store incoming faxes to (path as string folders separated by '/', leading and trailing '/' optional, required)
        """
        url = _get_url(self.base_url, 'SetOnlineStorageSettings', self.api_credentials, provider=provider, settings=settings)
        return _get(self.http, url)
    
    def set_password(self, password, hashFunction=None):
        """Set a new login password for the currently logged in user.
        You may use md5 encrypted passwords by setting the value of hashFunction to 'md5'.
        Note: password values must be lower case when using a hashFunction other than 'plain'!
        """
        url = _get_url(self.base_url, 'SetPassword', self.api_credentials, password=password, hashFunction=hashFunction)
        return _get(self.http, url)
    
    def set_profile_properties(self, profile, properties, ignoreerrors=None):
        """Saves values to an extended user profile
        Users may have different profiles. Use this method to store values in them.
        Profiles will be created if not present yet.
        """
        url = _get_url(self.base_url, 'SetProfileProperties', self.api_credentials, profile=profile, properties=properties, ignoreerrors=ignoreerrors)
        return _get(self.http, url)
    
    def validate_new_username(self, username, dictionary=None):
        """Validate a username for a new user.
        Returns a list of suggestions for the username if given username is already in use. Call this prior to UserInfo/CreateUser to show alternative usernames to the user if the entered username is already occupied or invalid.
        """
        url = _get_url(self.base_url, 'ValidateNewUsername', self.api_credentials, username=username, dictionary=dictionary)
        return _get(self.http, url)
