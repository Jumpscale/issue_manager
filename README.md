# IssueManager

IssueManager is a portal9 application used to provide a kanban overview for Issues.

## Installation
### Manual Installation
1- Make sure to have portal9 installed. (See: https://github.com/Jumpscale/portal9/blob/master/docs/GettingStarted/Installation.md)

2- Clone issue_manager (https://github.com/Jumpscale/issue_manager/)

3- Copy/link apps/IssueManager to your portal applications directory `opt/jumpscale9/apps/portals/main/base`


### Prefab Installation
`prefab.apps.issuemanager.install()`

### Using JumpScale bash

Using JumpScale bash it is possible to set up the environment to use IssueManager which includes JumpScale and portal installation.
Follow the install instruction [here](https://github.com/Jumpscale/bash/blob/master/README.md).
You can then run the command `ZInstall_issuemanager` that will install JumpScale, portal as well as setting up IssueManager.

## Howto sync data
See (https://docs.greenitglobe.com/gig/cockpit_issue_manager) for GIG internal setup.


### Syncing from Github:
You need to get client for your github.

```    
gl = j.clients.github.getClient(token)
gl.syncAllFromGithub(org1Name, org2Name, org3Name)
```
syncAllFromGithub will sync users, organizations, repos, and issues.

### Syncing from Gogs:
For GIG internals gogs data access and synchronization See (https://docs.greenitglobe.com/gig/cockpit_issue_manager)

In general you need to serialize data into a PostgreSQL instance with a valid gogs schema and then
generate capnp models in redis.

### Using the IssueManager macros

There are three macros for the issuemanager:
1. **kanbandata macro**
    * to use:
    ```
    {{kanbandata:issue }}
    ```
    This will show all issues sync'd in the issuemanager.

    * You can also filter on any attribute in the issue model (See bottom for a list of these attributes)
    ```python
    # Example:
    {{kanbandata:issue repo:org_support assignees:despiegk}}
    ```

2. **issue_reports macro**
    * to use
        * `groupon` tag is to choose which issue attribute to group the results by. Default is assignees
        * to filter, use the same syntax as the kanban macro
    ```python
    # use "groupon" to group the issues to form any report
    # use extra tags to filter. eg: "priority:critical" or "assignees:despiegk"
    {{issue_reports groupon:milestone}}
    ```

3. **issue_time_reports macro**
    * to use
        * `groupon` tag is to choose whether to groupon `creationTime` or `modTime`
        * `ranges` tag defines the ranges of time.

            eg: `4h,2d,4d` will create 4 groups for issues;
            1. from 4 hours ago
            2. 4 hours till 2 days ago
            3. 2 days ago till 4 days ago
            4. 4 days ago till the beginning.
        * to filter, use the same syntax as the kanban macro
    ```python
    # use "groupon" to choose grouping. Only creationTime and modTime are allowed
    # use "ranges" to define grouping ranges
    # use extra tags to filter. eg: "priority:critical" or "assignees:despiegk"
    {{issue_time_reports groupon:creationTime ranges:4h,2d,4d}}
    ```

_Use the jinja templating in the example reports to make your reports visual_

#### Issue attributes:
```
title: Text
repo: Text
milestone: Text #is name of milestone
assignees: Text # Name of user
isClosed: Boolean
labels: List(Text)
content: Text
organization: Text
modTime: epoch
creationTime epoch
state State;
    enum State {
        new
        inprogress
        resolved
        wontfix
        question
        closed
    }

priority Priority;
    enum Priority {
        minor
        normal
        major
        critical
    }

type Type;
    enum Type {
        unknown
        alert
        bug
        doc
        feature
        incident
        question
        request
        story
        task
    }
inGithub: Boolean;
```

## Screenshots

Application Home page
![HomePage](home.png)

Issues List
![Issues](issues.png)

Users list
![Users](users.png)

Kanban
![Kanban](kanban.png)


##
