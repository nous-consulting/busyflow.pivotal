import time
import pkg_resources
import datetime
from poster.encode import multipart_encode
from poster.encode import MultipartParam
from dateutil import parser
import httplib2
import urllib
import logging

from xmlbuilder import XMLBuilder
from xml.dom import minidom

log = logging.getLogger(__name__)


def error_from_response(http_response, error_class,
                        response_body=None, parsed_body=None):
  error = error_class('%s: %i, %s' % (http_response.reason, http_response.status,
                                      parsed_body if parsed_body else response_body))
  error.status = http_response.status
  error.reason = http_response.reason
  error.body = response_body
  error.parsed_body = parsed_body
  error.headers = http_response.items()
  return error


class Error(Exception):
  pass


class RequestError(Error):
    """Base http exception"""
    status = None
    reason = None
    body = None
    headers = None


class UnauthorizedError(RequestError):
    """Unauthorized exception"""


def parse(node):
    # determine type
    if node.attributes:
        obj_type = node.attributes["type"].value
    elif node.nodeName in ["stories", "notes"]:
        obj_type = "array"
    elif node.nodeName in ["labels"]:
        obj_type = "csv"
    elif len(node.childNodes) > 1:
        obj_type = "dictionary"
    else:
        obj_type = "string"
    return NODE_PARSERS.get(obj_type, parse_dict)(node)


def parse_csv(node):
    if len(node.childNodes) == 0:
        return []
    value = node.childNodes[0].wholeText.strip()
    return value.split(",")


_tzmap = None
def get_tzmap():
    global _tzmap
    if _tzmap is None:
        _tzmap = {}
        tzmap_file = pkg_resources.resource_string('busyflow.pivotal', 'tzmap.txt')
        for line in tzmap_file.splitlines():
            [short_name, long_name, offset] = line.split('\t')
            _tzmap[short_name] = offset
    return _tzmap


def parse_string_to_dt(value):
    try:
        time_tuple = time.strptime(value, '%Y/%m/%d %H:%M:%S %Z')
    except ValueError:
        try:
            parts = value.split(' ')
            dt = ' '.join(parts[:-1])
            tz = parts[-1]
            offset = get_tzmap().get(tz, '')
            time_tuple = parser.parse(dt + ' ' + offset).utctimetuple()
        except ValueError:
            time_tuple = time.strptime(dt, '%Y/%m/%d %H:%M:%S')
    return datetime.datetime(
        time_tuple.tm_year,
        time_tuple.tm_mon,
        time_tuple.tm_mday,
        time_tuple.tm_hour,
        time_tuple.tm_min,
        time_tuple.tm_sec)


def parse_datetime(node):
    if len(node.childNodes) == 0:
        return None
    value = node.childNodes[0].wholeText.strip()
    return parse_string_to_dt(value)


def parse_list(parent_node):
    new_list = []
    for child_node in parent_node.childNodes:
        if child_node.nodeName != "#text":
            value = parse(child_node)
            new_list.append(value)
    return new_list


def parse_dict(parent_node):
    new_dict = {}
    for child_node in parent_node.childNodes:
        if child_node.nodeName != "#text":
            value = parse(child_node)
            new_dict[child_node.nodeName] = value
    return new_dict


def parse_string(node):
    if not node.childNodes:
        return ""
    return node.childNodes[0].wholeText.strip()


NODE_PARSERS = {'array': parse_list,
                'string': parse_string,
                'dictionary': parse_dict,
                'integer': lambda node: int(node.childNodes[0].wholeText.strip()),
                'csv': parse_csv,
                'datetime': parse_datetime}


class Endpoint(object):
    def __init__(self, pivotal):
        self.pivotal = pivotal

    def _get(self, endpoint, **params):
        return self.pivotal._apicall(endpoint, 'GET', **params)

    def _post(self, endpoint, **params):
        return self.pivotal._apicall(endpoint, 'POST', **params)

    def _put(self, endpoint, **params):
        return self.pivotal._apicall(endpoint, 'PUT', **params)

    def _delete(self, endpoint, **params):
        return self.pivotal._apicall(endpoint, 'DELETE', **params)


class ProjectEndpoint(Endpoint):

    def get(self, project_id):
        return self._get("projects/%s" % project_id)

    def all(self):
        return self._get("projects")

    def activities(self, project_id, limit=None, occurred_since_date=None, newer_than_version=None):
        return self._get("projects/%s/activities" % project_id, limit=limit,
                         occurred_since_date=occurred_since_date,
                         newer_than_version=newer_than_version)

    def make_post_xml(self, name, iteration_length, point_scale):
        project = XMLBuilder(format=True)
        with project.project:
            if name is not None:
                project << ('name', name)
            if iteration_length is not None:
                project << ('iteration_length', iteration_length)
            if point_scale is not None:
                project << ('point_scale', point_scale)
        return str(project)

    def post(self, name, iteration_length, point_scale):
        # XXX actually test it, add missing attributes
        body = self.make_project_xml(name, iteration_length, point_scale)
        return self._post("projects", body=body)


class IterationEndpoint(Endpoint):

    def all(self, project_id, limit=None, offset=None):
        return self._get("projects/%s/iterations" % project_id, limit=limit, offset=offset)

    def done(self, project_id, limit=None, offset=None):
        return self._get("projects/%s/iterations/done" % project_id, limit=limit, offset=offset)

    def current(self, project_id, limit=None, offset=None):
        return self._get("projects/%s/iterations/current" % project_id, limit=limit, offset=offset)

    def backlog(self, project_id, limit=None, offset=None):
        return self._get("projects/%s/iterations/backlog" % project_id, limit=limit, offset=offset)

    def current_backlog(self, project_id, limit=None, offset=None):
        return self._get("projects/%s/iterations/current_backlog" % project_id, limit=limit, offset=offset)


class ActivityEndpoint(Endpoint):

    def all(self, limit=None, occurred_since_date=None, newer_than_version=None):
        return self._get("activities", limit=limit,
                         occurred_since_date=occurred_since_date,
                         newer_than_version=newer_than_version)


class TokenEndpoint(Endpoint):

    def active(self, username, password):
        return self._post('tokens/active',
                          username=username,
                          password=password)


class StoryEndpoint(Endpoint):

    def make_story_xml(self, name=None, description=None, story_type=None,
                       owned_by=None, requested_by=None, estimate=None, current_state=None, labels=None):
        story = XMLBuilder(format=True)
        with story.story:
            if name is not None:
                story << ('name', name)
            if description is not None:
                story << ('description', description)
            if requested_by is not None:
                story << ('requested_by', requested_by)
            if owned_by is not None:
                story << ('owned_by', owned_by)
            if story_type is not None:
                story << ('story_type', story_type)
            if estimate is not None:
                story << ('estimate', str(estimate), {'type': 'integer'})
            if current_state is not None:
                story << ('current_state', current_state)
            if labels is not None:
                label_string = ','
                if labels:
                    label_string = ','.join(labels)
                story << ('labels', label_string)

        return str(story)

    def make_comment_xml(self, text, author):
        x = XMLBuilder(format=True)
        with x.note:
            x << ('text', text)
            if author is not None:
                x << ('author', author)
        return str(x)

    def all(self, project_id, query=None, limit=None, offset=None):
        return self._get("projects/%s/stories" % project_id, query=query, limit=limit, offset=offset)

    def get(self, project_id, story_id):
        return self._get("projects/%s/stories/%s" % (project_id, story_id))

    def post(self, project_id, name, description, story_type,
             owned_by=None, requested_by=None, estimate=None,
             current_state=None, labels=None):
        body = self.make_story_xml(name, description, story_type,
                                   owned_by=owned_by,
                                   requested_by=requested_by,
                                   estimate=estimate,
                                   current_state=current_state,
                                   labels=labels)
        return self._post("projects/%s/stories" % project_id, body=body)

    def update(self, project_id, story_id,
               name=None, description=None, owned_by=None, requested_by=None,
               story_type=None, estimate=None, current_state=None, labels=None):
        body = self.make_story_xml(name, description, story_type,
                                   owned_by=owned_by,
                                   requested_by=requested_by,
                                   estimate=estimate,
                                   current_state=current_state,
                                   labels=labels)
        return self._put("projects/%s/stories/%s" % (project_id, story_id), body=body)

    def deliver_all_finished_stories(self, project_id):
        return self._put("projects/%s/stories/deliver_all_finished" % project_id)

    def delete(self, project_id, story_id):
        return self._delete("projects/%s/stories/%s" % (project_id, story_id))

    def move(self, project_id, story_id, target_id, move='after'):
        params = {}
        params['move[move]'] = move
        params['move[target]'] = target_id
        return self._post("projects/%s/stories/%s/moves" % (project_id, story_id),
                          **params)

    def add_comment(self, project_id, story_id, text, author=None):
        body = self.make_comment_xml(text, author)
        return self._post("projects/%s/stories/%s/notes" % (project_id, story_id), body=body)

    def add_attachment(self, project_id, story_id,
                       filename,
                       file_obj,
                       filetype,
                       filesize=None):
        if isinstance(file_obj, basestring):
            file_obj = open(file_obj, 'rb')
        file_data = MultipartParam(name='Filedata',
                                   filename=filename,
                                   filetype=filetype,
                                   fileobj=file_obj,
                                   filesize=filesize)

        params = {'Filedata': file_data}
        data, mp_headers = multipart_encode(params)

        if 'Content-Length' in mp_headers:
            mp_headers['Content-Length'] = str(mp_headers['Content-Length'])

        return self._post("projects/%s/stories/%s/attachments" % (project_id, story_id),
                          body="".join(list(data)),
                          headers=mp_headers)


class PivotalClient(object):

    def __init__(self, token,
                 base_url="https://www.pivotaltracker.com/services/v3/",
                 parse_xml=True, cache=None, timeout=None, proxy_info=None):
        self.token = token
        self.base_url = base_url
        self.parse_xml = parse_xml
        self.client = httplib2.Http(cache=cache, timeout=timeout, proxy_info=proxy_info)

        # connect endpoints
        self.projects = ProjectEndpoint(self)
        self.stories = StoryEndpoint(self)
        self.activities = ActivityEndpoint(self)
        self.iterations = IterationEndpoint(self)
        self.tokens = TokenEndpoint(self)

    def _apicall(self, endpoint, method, **params):
        url = '%s%s' % (self.base_url, endpoint)
        body = params.pop('body', '')
        _headers = params.pop('headers', {})
        cleaned_params = dict([(k, v) for k, v in params.iteritems() if v])

        headers = {'X-TrackerToken': self.token}
        if method in ['POST', 'PUT'] and body:
            headers['Content-type'] = 'application/xml'

        headers.update(_headers)

        if cleaned_params:
            assert not body # can't have body and parameters at the same time
            body = urllib.urlencode(cleaned_params)
            if method == 'GET':
                url = '%s?%s' % (url, body)
                body = ''

        resp, content = self.client.request(url, method=method, body=body, headers=headers)

        parsed_content = None
        try:
            parsed_content = self.parseContent(content)
        except ValueError:
            log.error(resp, content)

        error_cls = RequestError
        if resp.status == 401:
            error_cls = UnauthorizedError

        if resp.status != 200:
            raise error_from_response(resp, error_cls,
                                      content, parsed_content)

        if parsed_content is None:
            # generate the error once more
            self.parseContent(content)

        return parsed_content

    def parseContent(self, content):
        dom = minidom.parseString(content)
        if self.parse_xml:
            return parse_dict(dom)
        else:
            return dom
