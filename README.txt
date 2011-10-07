Pivotal API client library
==========================

Simple example
--------------

If you don't have a token, get one using username and password (or
just pass it directly):

  >>> client = PivotalClient(token=None, cache='path/to/cache')
  >>> token = client.token.active('username', 'password')['token']['guid']

  >>> client.token = token

Get some projects:

  >>> projects = client.projects.all()['projects']

Get current stories for a project:

  >>> iterations = client.iterations.current(projects[0]['id'])

  >>> storries_in_current_iteration = iterations[0]['iteration']['stories']

This should probably be client.projects.iterations.current(), but using
flat structure at the moment.

Missing methods and endpoints
-----------------------------

Members::

  GET http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/memberships
  POST http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/memberships
  GET http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/memberships/$MEMBERSHIP_ID
  DELETE http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/memberships/$MEMBERSHIP_ID

Project::

  POST http://www.pivotaltracker.com/services/v3/projects - missing parameters
  PUT http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/deliver_all_finished

Tasks::

  GET http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks/$TASK_ID
  GET http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks
  POST http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks?task\[description\]=clean%20shields
  PUT http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks/$TASK_ID
  DELETE http://www.pivotaltracker.com/services/v3/projects/$PROJECT_ID/stories/$STORY_ID/tasks/$TASK_ID

(TODO find out whether it is possible to pass parameters to stories/projects throught URL)
