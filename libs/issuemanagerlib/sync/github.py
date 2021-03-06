from js9 import j
from multiprocessing.pool import ThreadPool as Pool
from issuemanagerlib import issuemanager


# please note you need to use ModelBase1 for now.
def githubtimetoint(t):
    #parsed = datetime.strptime(t, "%Y-%m-%d %I:%M:%S")
    return j.data.time.any2epoch(t)


git_host_name = "github"


def fetchall_from_paginated_list(paginated_list):
    """
    Eagrly fetch all the items from paginated list (Github API paged responses)

    @param paginated_list PaginatedList: paginated list object.
    """
    els = []
    idx = 0
    while True:
        vals = paginated_list.get_page(idx)
        if not vals:
            break
        else:
            els.extend(vals)
            idx += 1
    return els


def fetchall_from_many_paginated_lists(*paginated_lists):
    """
    Fetch all items from many paginated lists and flatten them out.

    @param paginated_lists list: list of paginated lists objects.
    """
    els = []
    for p in paginated_lists:
        els.extend(fetchall_from_paginated_list(p))
    return els


class GithubSynchronizer:

    def __init__(self, githubclient):
        self.client = githubclient
        self.pool = Pool()
        self.model = None
        # issuemanager.set_namespaceandstore("github", "github")

        self.userCollection = issuemanager.getUserCollectionFromDB()
        self.orgCollection = issuemanager.getOrgCollectionFromDB()
        self.issueCollection = issuemanager.getIssueCollectionFromDB()
        self.repoCollection = issuemanager.getRepoCollectionFromDB()
        self.logger = j.logger.get('issuemanager.sync.github')

    @property
    def api(self):
        return self.client.api

    def getUsersFromGithubOrg(self, org):
        """
        populates user models from github organization.

        @param org str: organization name.

        """
        self.logger.info("get users from github org:%s" % org)
        org = self.api.get_organization(org)
        members_pagedlist = org.get_members()

        members = fetchall_from_paginated_list(members_pagedlist)

        for user in members:
            url = "https://github.com/%s" % user.login
            user_model = self.userCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=user.id, git_host_url=url)
            if user_model.dbobj.name != user.login:
                user_model.dbobj.name = user.login
                user_model.changed = True
            if user.name and user_model.dbobj.fullname != user.name:
                user_model.dbobj.fullname = user.name
                user_model.changed = True
            if user.email and user_model.dbobj.email != user.email:
                user_model.dbobj.email = user.email
                user_model.changed = True
            # user_model.gitHostRefSet(name=git_host_name, id=user.id)
            # if user_model.dbobj.iyoId != user.login:
            #     user_model.dbobj.iyoId = user.login
                # user_model.changed = True
            if not user_model.dbobj.inGithub:
                user_model.dbobj.inGithub = True
                user_model.changed = True
            user_model.save()

            self.client.users[user.login] = user_model.key

    # FIX ALL NR_FIELDS TO USE totalCount attr
    def _getOrganizationFromGithub(self, orgname):
        """
        populate organization model from Github organization name.

        @param orgname str: organization name.
        """
        if not self.client.users:
            self._getUsersFromGithubOrg(git_host_name, orgname)

        org = self.api.get_organization(orgname)
        allissues = fetchall_from_paginated_list(org.get_issues())
        nrissues = len(allissues)

        orgid = org.id

        url = 'https://github.com/%s' % orgname
        org_model = self.orgCollection.getFromGitHostID(
            git_host_name=git_host_name, git_host_id=org.id, git_host_url=url)

        # org_model.dbobj.repos = reposids

        # repos = fetchall_from_paginated_list(org.get_repos())
        # if org_model.dbobj.repos != repos:
        #     org_model.initSubItem("repos")
        #     org_model.list_repos = repos
        #     org_model.changed = True

        # milestones = set([m.title for m in fetchall_from_many_paginated_lists(*[rep.get_milestones() for rep in repos])])
        #  nr of milestones => set of all milestones in all repos?
        # nrmilestones = len(milestones)

        description = orgname  # FIXME: how to get a description of an org? orgname used instead.

        members = fetchall_from_paginated_list(org.get_members())
        nrmembers = len(members)
        members = [self.client.users[item.login]
                   for item in members]
        members = members.sort()

        # FIXME: calculate owners ids list.
        owners = []

        if org_model.dbobj.members != members:
            org_model.initSubItem("members")
            org_model.list_members = members
            org_model.changed = True

        if org_model.dbobj.name != orgname:
            org_model.dbobj.name = orgname
            org_model.changed = True

        # org_model.dbobj.owners = owners
        # org_model.dbobj.key = orgid
        org_model.dbobj.inGithub = True
        org_model.dbobj.description = org.raw_data['description'] or ''
        org_model.save()

    def getUsersFromGithubOrgs(self, *orgs):
        """
        Populates user models from a list of github organizations.

        @param orgs list: list of organizations names.

        """
        self.pool.map(self.getUsersFromGithubOrg, orgs)
        # from IPython import embed
        # print("DEBUG NOW oi")
        # embed()
        # raise RuntimeError("stop debug here")

    def getOrgsFromGithub(self, *orgs):
        """
        Populates organization models from github organizations names list.

        @param orgs list: list of organizations names.
        """
        self.pool.map(self._getOrganizationFromGithub, orgs)

    def getIssuesFromGithubRepo(self, repo):
        """
        Populates issues models from github repo.

        @param repo str: github repository name.

        """
        if not self.client.repos:
            self.getReposFromGithubOrgs(git_host_name)

        repo = self.api.get_repo(repo)

        def process_issue_from_github(issue):
            """
            Process issue from github issue.

            @param issue Issue: issue object.
            """

            url = 'https://github.com/%s/issues/%s' % (issue.repository.full_name, issue.number)
            issue_model = self.issueCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=issue.id, git_host_url=url)
            issue_model.dbobj.assignees = [self.client.users[user.login] for user in issue.assignees]

            # our view has pre-aggregrated the comments, need to do some minimal parsing now
            comments = fetchall_from_paginated_list(issue.get_comments())
            # comments.sort(key=lambda comment:comment.id)  # will make sure its
            # sorted on comment_id (prob required for right order of comments)
            if comments != []:
                for comment in comments:
                    issue_model.commentSet(comment.body, owner=self.client.users.get(comment.user.login))

            issue_model.dbobj.milestone = issue.milestone.title if issue.milestone else ''

            issue_model.dbobj.labels = [label.name for label in issue.labels]
            issue_model.dbobj.title = issue.title or ''
            issue_model.dbobj.content = issue.body.replace('!', '\!') if issue.body else ''
            issue_model.dbobj.isClosed = issue.state == 'closed'
            issue_model.dbobj.repo = self.client.repos[issue.repository.full_name]
            issue_model.dbobj.inGithub = True
            issue_model.changed = True
            issue_model.save()

        issues = fetchall_from_paginated_list(repo.get_issues())
        pool = Pool(50)
        pool.map(process_issue_from_github, issues)

    def getIssuesFromGithubOrganization(self, org):
        """
        Populates all issues from github organization org

        @param org str: organization name.
        """
        org = self.api.get_organization(org)
        repos = fetchall_from_paginated_list(org.get_repos())
        repos = [rep.full_name for rep in repos]
        self.pool.map(self.getIssuesFromGithubRepo, repos)

    def getIssuesFromGithubOrganizations(self, *orgs):
        """
        Populates all issues from github organizations list orgs.

        @param orgs list[str]: list of organizations names.
        """
        self.pool.map(self.getIssuesFromGithubOrganization, orgs)

    def getReposFromGithubOrgs(self, *orgs):
        """
        Populate repos models from list of organizations names.

        @param orgs list[str]: list of organizations names.

        """
        self.pool.map(self.getReposFromGithubOrg, orgs)

    def getReposFromGithubOrg(self, org):
        """
        Populates repos from organization.

        @param org str: organization names.

        """
        org = self.api.get_organization(org)
        repos = fetchall_from_paginated_list(org.get_repos())

        def process_repo_from_github(repo):
            """
            Process issue from github issue.

            @param issue Issue: issue object.
            """
            labels = fetchall_from_paginated_list(repo.get_labels())
            milestones = fetchall_from_paginated_list(repo.get_milestones())
            issues = fetchall_from_paginated_list(repo.get_issues())

            url = 'https://github.com/%s' % repo.full_name
            repo_model = self.repoCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=repo.id, git_host_url=url)

            repo_model.dbobj.name = repo.name
            repo_model.dbobj.description = repo.description or ''
            repo_model.dbobj.owner = self.client.users.get(repo.owner.name, '')
            repo_model.dbobj.nrIssues = len(issues)
            repo_model.dbobj.nrMilestones = len(milestones)
            repo_model.inGithub = True
            repo_model.changed = True
            repo_model.save()

            self.client.repos[repo.full_name] = repo_model.key
        pool = Pool(50)
        pool.map(process_repo_from_github, repos)

    # def getRepoFromGithubRepo(self, git_host_name, repo):
    #     """
    #     Populate repo model from github repository.
    #
    #     @param repo str: repository name.
    #     """
    #
    #
    #     repoid = repo.id
    #     labels = fetchall_from_paginated_list(repo.get_labels())
    #     milestones = fetchall_from_paginated_list(repo.get_milestones())
    #
    #     url = "https://github.com/%s" % repo
    #     repo_model = self.repoCollection.getFromGitHostID(git_host_name=git_host_name, git_host_id=repoid, git_host_url=url)
    #     # repo_model.dbobj.labels = [lbl.name for lbl in labels]
    #
    #
    #     # HOW TO CALCULATE THE MEMBERS OF REPO? or should check the members of the team in it's parent org?
    #     members = []
    #     repoorg = repo.organization
    #     if repoorg.name is not None:
    #         members = fetchall_from_paginated_list(repoorg.get_members())
    #     repo_model.dbobj.members = []
    #     for member in members:
    #         member_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Member, userKey=str(member.id), access=0)
    #         repo_model.dbobj.members.append(member_scheme)

        # repo_model.dbobj.milestones = []
        # for milestone in milestones:
        #     nrclosedissues = milestone.closed_issues
        #     nropenissues = milestone.open_issues
        #     nrallissues = nropenissues + nrclosedissues
        #     ncomplete = 100
        #     if nrallissues>0:
        #         ncomplete = int(100*nrclosedissues/nrallissues)
        #     md = {
        #         "name": milestone.title,
        #         "id": milestone.id,
        #         "deadline": githubtimetoint(milestone.due_on),
        #         "isClosed": milestone.state!="open",
        #         "nrIssues": nropenissues + nrclosedissues,
        #         "nrClosedIssues": nrclosedissues,
        #         "completeness" : ncomplete #ceil(nrClosedIssuesForThisMilestone/); #in integer (0-100)
        #     }
        #     milestone_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Milestone, **md)
        #     milestone_scheme.id = milestone.id
        #     repo_model.dbobj.milestones.append(milestone_scheme)

        # repo_model.dbobj.name = repo.name
        # repo_model.dbobj.description = repo.name
        # repo_model.dbobj.nrIssues = len(repo.issues)
        # repo_model.dbobj.nrMilestones = len(milestones)
        # repo_model.dbobj.inGithub = True
        # repo_model.save()

    def syncAllFromGithub(self, *orgs):
        self.getUsersFromGithubOrgs(*orgs)
        self.getOrgsFromGithub(*orgs)
        self.getReposFromGithubOrgs(*orgs)
        self.getIssuesFromGithubOrganizations(*orgs)


if __name__ == "__main__":
    import os
    if "GITTOKEN" not in os.environ:
        raise j.exceptions.Input(
            message="Please do 'export GITTOKEN=???' to set your gittoken in env variables, then restart this script.", level=1, source="", tags="", msgpub="")

    GITTOKEN = os.environ["GITTOKEN"]
    githubclient = j.clients.github.getClient(GITTOKEN)
    githubsync = GithubSynchronizer()
    githubsync.syncAllFromGithub("jumpscale")
