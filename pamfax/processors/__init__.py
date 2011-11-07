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

import logging
import mimetypes
import os
import socket

IP_ADDR = socket.gethostbyname(socket.gethostname())
USER_AGENT = 'dynaptico-pamfax'
ORIGIN = 'script'
CONTENT_TYPE = 'content-type'
CONTENT_TYPE_JSON = 'application/json'

logger = logging.getLogger('pamfax')

# ----------------------------------------------------------------------------
# "private" helper methods
# ----------------------------------------------------------------------------

def _get_url(base_url, action, api_credentials, **kwargs):
    """Construct the URL that corresponds to a given action.
    All kwargs whose value is None are filtered out.
    
    Arguments: 
    base_url -- The base of the URL corresponding to the PamFax processor name
    action -- The PamFax method to append to the base URL
    api_credentials -- The API credentials including user token extracted from /Session/VerifyUser
    
    Keyword arguments:
    **kwargs -- optional HTTP parameters to send to the PamFax URL
    
    """
    url = '%s/%s%s' % (base_url, action, api_credentials)
    if len(kwargs) == 0:
        return url
    query = {}
    for arg in kwargs:
        kwarg = kwargs[arg]
        if kwarg is not None:
            if isinstance(kwarg, list):
                for i in range(0, len(kwarg)):
                    query['%s[%d]' % (arg, i)] = kwarg[i]
            else:
                query[arg] = kwarg
    url = '%s&%s' % (url, urlencode(query))
    return url

def _get_and_check_response(http):
    """Wait for the HTTP response and throw an exception if the return 
    status is not OK. Return either a dict based on the 
    HTTP response in JSON, or if the response is not in JSON format,
    return a tuple containing the data in the body and the content type.
    
    """
    response = http.getresponse()
    codes = (response.status, response.reason)
    content = response.read()
    logger.debug('%s\n%s', codes, content)
    if response.status != 200:
        raise HTTPException("Response from server not OK: %s %s" % codes)
    content_type = response.getheader(CONTENT_TYPE, None)
    if content_type is not None and content_type.startswith(CONTENT_TYPE_JSON):
        return jsonlib.loads(content)
    else:
        return (content, content_type)

def _get(http, url, body=''):
    """Gets the specified url and returns the response."""
    logger.info("getting url '%s' with body '%s'", url, body)
    http.request('GET', url, body)
    return _get_and_check_response(http)

def _post(http, url, body, headers={}):
    """Posts to the specified url and returns the response."""
    logger.info("posting to url '%s' with body '%s'", url, body)
    http.request('POST', url, body, headers)
    return _get_and_check_response(http)

def _encode_multipart_formdata(fields, files):
    """Encode multipart form data per mime spec and return (content_type, body)
    
    Arguments:
    fields -- A sequence of (name, value) elements for regular form fields.
    files -- A sequence of (name, filename, value) elements for data to be uploaded as files
    
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
        
        Arguments:
        file_uuid -- The uuid of the file to get
        
        """
        url = _get_url(self.base_url, 'GetFile', self.api_credentials, file_uuid=file_uuid)
        return _get(self.http, url)
    
    def get_geo_ip_information(self, ip):
        """Returns Geo information based on the given IP address (IPV4)
        
        Arguments:
        ip -- the ip to get geo information off
        
        """
        url = _get_url(self.base_url, 'GetGeoIPInformation', self.api_credentials, ip=ip)
        return _get(self.http, url)
    
    def get_page_preview(self, uuid, page_no, max_width=None, max_height=None):
        """Returns a preview page for a fax.
        
        May be in progress, sent or from inbox.
        
        Arguments:
        uuid -- The uuid of the fax to get preview for
        page_no -- Page number to get (1,2,...)
        max_width -- Maximum width in Pixel
        max_height -- Maximum height in Pixel
        
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
        
        Arguments:
        zone -- Zone of the country which is wanted (1-7)
        
        """
        url = _get_url(self.base_url, 'ListCountriesForZone', self.api_credentials, zone=zone)
        return _get(self.http, url)
    
    def list_currencies(self, code=None):
        """Returns the list of supported currencies.
        
        Result contains convertion rates too.
        If code is given will only return the specified currency's information.
        
        Keyword arguments:
        code -- CurrencyCode
        
        """
        url = _get_url(self.base_url, 'ListCurrencies', self.api_credentials, code=code)
        return _get(self.http, url)
    
    def list_languages(self, min_percent_translated=None):
        """List all available languages.
        
        Result may be filtered tso that only languages are returned that are
        at least translated $min_percent_translated %
        
        Keyward arguments:
        min_percent_translated -- the percentage value the languages have to be translated
        
        """
        url = _get_url(self.base_url, 'ListLanguages', self.api_credentials, min_percent_translated=min_percent_translated)
        return _get(self.http, url)
    
    def list_strings(self, ids, culture=None):
        """Returns a list of strings translated into the given language.
        
        Arguments:
        ids -- array of String identifiers. You may also pass a comma separated list as $ids[0] (ids[0]=BTN_YES,BTN_NO).
        
        Keyword arguments:
        culture -- culture identifier, defaults to users culture. Accepts full culture-codes like en-US, de-DE and just a language code like en, de, ...
        
        """
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
        """Add a note (free text) to the fax
        
        Arguments:
        fax_uuid -- uuid of the fax
        note -- text to add to the fax
        
        """
        url = _get_url(self.base_url, 'AddFaxNote', self.api_credentials, fax_uuid=fax_uuid, note=note)
        return _get(self.http, url)
    
    def count_faxes(self, type):
        """Returns the number of faxes from users history with a specific state.
        
        Arguments:
        type -- Possible values: history, inbox, inbox_unread, outbox or unpaid
        
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
        """Moves faxes to the trash.
        
        If siblings_too is true will perform for the given faxes and all other recipients
        from the same fax jobs.
        siblings_too will only be evaluated for uuids beloging to an outgoing fax and will be
        ignored for incoming faxes uuids
        
        """
        url = _get_url(self.base_url, 'DeleteFaxes', self.api_credentials, uuids=uuids, siblings_too=siblings_too)
        return _get(self.http, url)
    
    def delete_faxes_from_trash(self, uuids):
        """Removes faxes from trash
        
        This method is similar to EmptyTrash() which deletes all the faxes from trash
        
        Arguments:
        uuids -- ids of faxes to be removed vom trash
        
        """
        url = _get_url(self.base_url, 'DeleteFaxesFromTrash', self.api_credentials, uuids=uuids)
        return _get(self.http, url)
    
    def empty_trash(self):
        """Removes all faxes from trash for user and if user is member of a company and has delete rights also for the owners inbox faxes"""
        url = _get_url(self.base_url, 'EmptyTrash', self.api_credentials)
        return _get(self.http, url)
    
    def get_fax_details(self, uuid):
        """Returns the details of a fax in progress.
        
        Arguments:
        uuid -- UUID of the fax to show
        
        """
        url = _get_url(self.base_url, 'GetFaxDetails', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def get_fax_group(self, uuid):
        """Returns a fax groups details.
        
        Arguments:
        uuid -- Uuid of one of the faxes in the group.
        
        """
        url = _get_url(self.base_url, 'GetFaxGroup', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def get_inbox_fax(self, uuid, mark_read=None):
        """Returns the details of a fax in the inbox.
        
        Arguments:
        uuid -- UUID of the fax to show
        mark_read -- If true marks the fax as read (default: false).
        
        """
        url = _get_url(self.base_url, 'GetInboxFax', self.api_credentials, uuid=uuid, mark_read=mark_read)
        return _get(self.http, url)
    
    def get_transmission_report(self, uuid):
        """Get a .pdf-Version of a transmission report.
        
        On the transmission report basic data of the fax and a preview of the first page is shown.
        Should always be called with API_MODE_PASSTHRU, as the result is the pdf as binary data
        
        Arguments:
        uuid -- @attribute[RequestParam('uuid','string')]
        
        """
        url = _get_url(self.base_url, 'GetTransmissionReport', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def list_fax_group(self, uuid, current_page=None, items_per_page=None):
        """Lists all faxes in a group (that are sent as on job).
        
        Arguments:
        uuid -- Uuid of one of the faxes in the group.
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
        url = _get_url(self.base_url, 'ListFaxGroup', self.api_credentials, uuid=uuid, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_fax_notes(self, fax_uuid):
        """Lists all notes for the given fax in reverse order (latest first)
        
        Arguments:
        fax_uuid -- uuid of the fax to list notes for
        
        """
        url = _get_url(self.base_url, 'ListFaxNotes', self.api_credentials, fax_uuid=fax_uuid)
        return _get(self.http, url)
    
    def list_inbox_faxes(self, current_page=None, items_per_page=None):
        """List all faxes in the inbox of the current user.
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
        url = _get_url(self.base_url, 'ListInboxFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_outbox_faxes(self, current_page=None, items_per_page=None):
        """Faxes in the outbox that are currently in the sending process
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
        url = _get_url(self.base_url, 'ListOutboxFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_recent_faxes(self, count=None, data_to_list=None):
        """Returns a list of latest faxes for the user.
        
        Does not contain deleted and delayed faxes (See ListTrash for deleted faxes).
        
        Keyword arguments:
        count -- The count of items to return. Valid values are between 1 and 100
        data_to_list -- Any message types you want this function to return. Allowed models are 'sent', 'inbox', 'outbox'. Leave empty to get faxes of any type.
        
        """
        url = _get_url(self.base_url, 'ListRecentFaxes', self.api_credentials, count=count, data_to_list=data_to_list)
        return _get(self.http, url)
    
    def list_sent_faxes(self, current_page=None, items_per_page=None):
        """List all sent faxes (successful or not)
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
        url = _get_url(self.base_url, 'ListSentFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_trash(self, current_page=None, items_per_page=None):
        """List all faxes in trash
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
        url = _get_url(self.base_url, 'ListTrash', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def list_unpaid_faxes(self, current_page=None, items_per_page=None):
        """Lists all unpaid faxes that are waiting for a payment.
        
        When this user makes a transaction to add credit, these faxes will be sent automatically
        if they are younger that 2 hours.
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
        url = _get_url(self.base_url, 'ListUnpaidFaxes', self.api_credentials, current_page=current_page, items_per_page=items_per_page)
        return _get(self.http, url)
    
    def restore_fax(self, uuid):
        """Restores a fax from the trash.
        
        Arguments:
        uuid -- uuid of fax to restore
        
        """
        url = _get_url(self.base_url, 'RestoreFax', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def set_fax_read(self, uuid):
        """Sets a fax' read date to current time.
        
        Fax needs to be a fax in the inbox.
        
        Arguments:
        uuid -- uuid of fax to set as read
        
        """
        url = _get_url(self.base_url, 'SetFaxRead', self.api_credentials, uuid=uuid)
        return _get(self.http, url)
    
    def set_faxes_as_read(self, uuids):
        """Sets the read date of all the faxes to the current time
        
        Arguments:
        uuids -- array of uuids for faxes to set as read
        
        """
        url = _get_url(self.base_url, 'SetFaxesAsRead', self.api_credentials, uuids=uuids)
        return _get(self.http, url)
    
    def set_spam_state_for_faxes(self, uuids, is_spam=None):
        """Sets the spamscore for all the faxes depending on the flag "is_spam"
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
        
        Requires the file to be uploaded as POST parameter named 'file' as a standard HTTP upload. This could be either Content-type: multipart/form-data with file content as base64-encoded data or as Content-type: application/octet-stream with just the binary data.
        See http://www.faqs.org/rfcs/rfc1867.html for documentation on file uploads.
        
        Arguments:
        filename -- Name of the file. You can also use the same file name for each file (i.e "fax.pdf")
        
        Keyword arguments:
        origin -- Optional file origin (ex: photo, scan,... - maximum length is 20 characters).
        
        """
        file = open(filename, 'rb')
        basename = os.path.basename(file.name)
        content_type, body = _encode_multipart_formdata([('filename', basename)], [('file', basename, file.read())])
        url = _get_url(self.base_url, 'AddFile', self.api_credentials, filename=basename, origin=origin)
        return _post(self.http, url, body, {'Content-Type': content_type, 'Content-Length': str(len(body))})
    
    def add_file_from_online_storage(self, provider, uuid):
        """Add a file identified by an online storage identifier.
        
        You'll have to use the OnlineStorageApi to identify a user for an online storage provider first
        and then get listings of his files. These will contain the file identifiers used by this method.
        
        Arguments:
        provider -- Identifies the provider used (see OnlineStorageApi)
        uuid -- Identifies the file to be added (see OnlineStorageApi)
        
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
        """Clones an already sent fax in the API backend and returns it.
        
        Arguments:
        uuid -- The uuid of the source fax
        
        Keyword arguments:
        user_ip -- The IP address of the client (if available). Put your own IP address otherwise.
        user_agent -- User agent string of the client device. If not available, put something descriptive (like "iPhone OS 2.2")
        
        """
        url = _get_url(self.base_url, 'CloneFax', self.api_credentials, uuid=uuid, user_ip=user_ip, user_agent=user_agent)
        return _get(self.http, url)
    
    def create(self, user_ip=IP_ADDR, user_agent=USER_AGENT, origin=ORIGIN):
        """Creates a new fax in the API backend and returns it.
        
        If a fax job is currently in edit mode in this session, this fax job is returned instead.
        Note: This is not an error. It provides you with the possibility to continue with the fax.
        
        Keyword arguments:
        user_ip -- The IP address of the client (if available). Put your own IP address otherwise.
        user_agent -- User agent string of the client device. If not available, put something descriptive (like "iPhone OS 2.2")
        origin -- From where was this fax started? i.e. "printer", "desktop", "home", ... For reporting and analysis purposes.
        
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
        """Returns the recipients for the current fax.
        
        Keyword arguments:
        current_page -- The page which should be shown
        items_per_page -- How many items are shown per page
        
        """
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
        
        Only successful if all necessary data is set to the fax: at least 1 recipient and a cover page or a file uploaded.
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
        
        Keyword arguments:
        save_defaults -- Save Notification-Settings to user's Profile
        
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
        
        Arguments:
        faxnumber -- The faxnumber to query (incl countrycode: +12139851886, min length: 8)
        
        """
        url = _get_url(self.base_url, 'GetNumberInfo', self.api_credentials, faxnumber=faxnumber)
        return _get(self.http, url)
    
    def get_page_price(self, faxnumber):
        """Calculate the expected price per page to a given fax number.
        
        Use GetNumberInfo when you do not need pricing information, as calculating expected price takes longer then just looking up the info for a number.
        
        Arguments:
        faxnumber -- The faxnumber to query (incl countrycode: +12139851886, min length: 8). Login user first to get personalized prices.
        
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
        
        Arguments:
        provider -- Provider name. See OnlineStorage::ListProviders for available providers.
        username -- The user's name/login for the provider
        password -- User's password to access his data at the provider side
        
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
        
        Arguments:
        provider -- Provider name
        token -- Associative array with token information
        username -- Optional username (for displaying purposes)
        
        """
        url = _get_url(self.base_url, 'SetAuthToken', self.api_credentials, provider=provider, token=token, username=username)
        return _get(self.http, url)

# ----------------------------------------------------------------------------
# Session
# ----------------------------------------------------------------------------

class Session:
    """Class encapsulating a PamFax session"""
    
    def __init__(self, api_credentials, http):
        """Instantiates the Session class."""
        self.base_url = '/Session'
        self.api_credentials = api_credentials
        self.http = http
    
    def create_login_identifier(self, user_ip=None, timetolifeminutes=None):
        """Creates an identifier for the current user, which then can be passed to the portal to directly log in the user: https://portal.pamfax.biz/?_id=
        
        Be aware that these identifiers are case sensitive. Identifiers with ttl > 0 can only be used once.
        
        Keyword arguments:
        user_ip -- The IP address of the client on which this identifier will be bound to. Using the identfier from a different ip address will fail
        timetolifeminutes -- Optional a lifetime of this identifier. Defaults to 60 seconds. If <= 0 is given, the identifier does not expire and can be used more then once, but are tied to your current API key and can not be passed to online shop, portal, ... in the url
        
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
        """Registers listeners for the current session. Any change of the listened types will then be available via Session::ListChanges function
        
        Arguments:
        listener_types -- Array of types to be registered ('faxall','faxsending','faxsucceeded','faxfailed','faxretrying')
        
        """
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
        """Verifies a user via username/password
        
        Arguments:
        username -- Username of the user or the md5 of user's username. That's what he has entered when he registered
        password -- The password (or the md5 of the password) that the user entered in the registration process for the given username (case sensitive)
        
        """
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
        
        Arguments:
        amount -- The amount of credit you want to add to the current user's pamfax credit. Currency is the user's currency. You can also pass a negative value to remove credit from user for testing.
        
        Keyword arguments:
        reason -- Optionally add some reason why you added this credit
        
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
        
        Arguments:
        ip_address -- IP-Address to find nearest number for
        
        """
        url = _get_url(self.base_url, 'GetNearestFaxInNumber', self.api_credentials, ip_address=ip_address)
        return _get(self.http, url)
    
    def get_shop_link(self, type=None, product=None, pay=None):
        """Returns different shop links.
        
        Use these links to open a browser window with the shop in a specific state.
        
        Keyword arguments:
        type -- Type of link to return. Available: '', credit_packs, basic_plan, pro_plan, checkout
        product -- Product to add. Available: '',BasicPlan12,ProPlan12,OnDemand,Pack10,Pack30,Pack50,Pack100,Pack250,Pack500,Pack1000
        pay -- (DEPRECATED) direct leads to checkout page
        
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
        
        Arguments:
        vouchercode -- The voucher code. Format is ignored.
        
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
        """Create a new PamFax user and logs him in
        
        Arguments:
        name -- First and last name of the user
        username -- Unique username. Call will fail with bad_username error if the username already exists. Min 6 chars, max 60 chars. Can be left empty if externalprofile is given. Then the username will be generated from externalprofile. You could use UserInfo::ValidateNewUsername to create a unique username first and then pass it to this call
        password -- a password for the user. If left empty, a new password will be generated. Min 8 chars, max 20 chars. If length is 32, it's assumed as md5 of original password. Please then check min and max length by yourself!
        email -- A valid email address for this user.
        culture -- The culture of the user (en-US, de-DE, ...)
        
        Keyword arguments:
        externalprofile -- External profile data. externalprofile["type"] is the type of data: skype. externalprofile["client_ip"] should be set to the user's ip address
        campaign_id -- is used to payout recommendation bonus to given user uuid. i.e if user clicked on links like http://www.pamfax.biz/?ref=b36d019d53ba, the b36d019d53ba should be passed as campaign_id
        
        """
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
        """Returns avatars for current user
        
        Keyword arguments:
        provider -- Provider to load Image from
        
        """
        url = _get_url(self.base_url, 'GetUsersAvatar', self.api_credentials, provider=provider)
        return _get(self.http, url)
    
    def has_avatar(self):
        """Return if Avatar is available or not"""
        url = _get_url(self.base_url, 'HasAvatar', self.api_credentials)
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
        """Return the inboxes of the user with some additional data (like expiration).
        
        Keyword arguments:
        expired_too -- If true, lists all expired numbers too.
        
        """
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
        
        Keyword arguments:
        max -- How many results (5-20, default 5)
        
        """
        url = _get_url(self.base_url, 'ListUserAgents', self.api_credentials, max=max)
        return _get(self.http, url)
    
    def list_wall_messages(self, count=None, data_to_list=None):
        """Returns a list of activities for the user
        
        This list contains report about what has been happened lately in users account
        (like messages sent to the user, faxes sent, faxes received, orders placed, ...)
        
        Keyword arguments:
        count -- The count of items to return. Valid values are between 1 and 100
        data_to_list -- Any message types you want this function to return. Allowed models are 'faxsent', 'faxin', 'faxout', 'payment', 'message' and 'news'. Leave empty to get messages of any type.
        
        """
        url = _get_url(self.base_url, 'ListWallMessages', self.api_credentials, count=count, data_to_list=data_to_list)
        return _get(self.http, url)
    
    def save_user(self, user=None, profile=None):
        """Saves user profile
        
        Keyword arguments:
        user -- Users settings as associative array
        profile -- UserProfiles properties as associative array
        
        """
        url = _get_url(self.base_url, 'SaveUser', self.api_credentials, user=user, profile=profile)
        return _get(self.http, url)
    
    def send_message(self, body, type=None, recipient=None, subject=None):
        """Send a message to the user
        
        Arguments:
        body -- The message body
        
        Keyword arguments:
        type -- Type of message to send. Currently implemented: email, skypechat or sms
        recipient -- Recipient of the message. Might be an email address, IM username or phone number depending on the message type
        subject -- Optionally a subject. Not used in all message types (likely not used in SMS and chat)
        
        """
        url = _get_url(self.base_url, 'SendMessage', self.api_credentials, body=body, type=type, recipient=recipient, subject=subject)
        return _get(self.http, url)
    
    def send_password_reset_message(self, username, user_ip=None):
        """Send a password reset message to a user
        
        Arguments:
        username -- PamFax username to send the message to
        
        """
        url = _get_url(self.base_url, 'SendPasswordResetMessage', self.api_credentials, username=username, user_ip=user_ip)
        return _get(self.http, url)
    
    def set_online_storage_settings(self, provider, settings):
        """Sets users OnlineStorage settings.
        
        Expects the settings to be given as key-value pairs.
        Currently supported settings are:
            - inbox_enabled: Store incoming faxes (0|1, required)
            - inbox_path: Path to store incoming faxes to (path as string folders separated by '/', leading and trailing '/' optional, required)
        
        Arguments:
        provider -- Provider store settings for (see OnlineStorageApi::ListProviders)
        settings -- Key-value pairs of settings.
        
        """
        url = _get_url(self.base_url, 'SetOnlineStorageSettings', self.api_credentials, provider=provider, settings=settings)
        return _get(self.http, url)
    
    def set_password(self, password, hashFunction=None, old_password=None):
        """Set a new login password for the currently logged in user.
        
        You may use md5 encrypted passwords by setting the value of hashFunction to 'md5'.
        Note: password values must be lower case when using a hashFunction other than 'plain'!
        
        Arguments:
        password -- The new password. Needs to be between 6 and 60 chars long
        
        Keyword arguments:
        hashFunction -- The function used to enrycpt the password. Allowed values: plain or md5.
        old_password -- The current password. This is optional for the moment but will be required in future versions. Note that the $hashFunction value applies to this argument too.
        
        """
        url = _get_url(self.base_url, 'SetPassword', self.api_credentials, password=password, hashFunction=hashFunction, old_password=old_password)
        return _get(self.http, url)
    
    def set_profile_properties(self, profile, properties, ignoreerrors=None):
        """Saves values to an extended user profile
        
        Users may have different profiles. Use this method to store values in them.
        Profiles will be created if not present yet.
        
        Arguments:
        properties -- key=>value pairs of all profiles properties to save
        
        Keyword arguments:
        ignoreerrors -- If a field can not be found in the profile object, just ignore it. Otherwise returns an error
        
        """
        url = _get_url(self.base_url, 'SetProfileProperties', self.api_credentials, profile=profile, properties=properties, ignoreerrors=ignoreerrors)
        return _get(self.http, url)
    
    def validate_new_username(self, username, dictionary=None):
        """Validate a username for a new user.
        
        Returns a list of suggestions for the username if given username is already in use. Call this prior to UserInfo/CreateUser to show alternative usernames to the user if the entered username is already occupied or invalid.
        
        Arguments:
        username -- Unique username to validate. Call will fail with bad_username error if the username already exists. Min 6 chars, max 60 chars.
        
        """
        url = _get_url(self.base_url, 'ValidateNewUsername', self.api_credentials, username=username, dictionary=dictionary)
        return _get(self.http, url)
