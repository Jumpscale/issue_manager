def gitHostRefSet(model, git_host_name, git_host_id, git_host_url):
    """
    @param name is name of gogs instance
    @id is id in gogs
    """
    model.logger.debug("gitHostRefSet: git_host_name='%s' git_host_id='%s' git_host_url='%s'" %
                       (git_host_name, git_host_id, git_host_url))
    ref = gitHostRefGet(model, git_host_name, git_host_url)
    if ref is None:
        model.addSubItem("gitHostRefs", data=model.collection.list_gitHostRefs_constructor(
            id=git_host_id, name=git_host_name, url=git_host_url))
        # key = model.collection._index.lookupSet("githost_%s" % git_host_name, git_host_id, model.key)
        model.save()
    else:
        if str(ref.id) != str(id):
            raise j.exceptions.Input(
                message="gogs id has been changed over time, this should not be possible",
                level=1,
                source="",
                tags="",
                msgpub="")

def gitHostRefExists(model, git_host_name):
    return not gitHostRefGet(model, git_host_name) is None

def gitHostRefGet(model, git_host_name, git_host_url):
    for item in model.dbobj.gitHostRefs:
        if item.name == git_host_name:
            return item
    return None

def getFromGitHostID(modelCollection, git_host_name, git_host_id, git_host_url, createNew=True):
    """
    @param git_host_name is the name of the gogs instance
    """
    modelCollection.logger.debug("gitHostRefSet: git_host_name='%s' git_host_id='%s' git_host_url='%s'" % (
        git_host_name, git_host_id, git_host_url))
    key = modelCollection._index.lookupGet("githost_%s" % git_host_name, git_host_id)
    if key is None:
        modelCollection.logger.debug("githost id not found, create new")
        if createNew:
            modelActive = modelCollection.new()
            gitHostRefSet(model=modelActive, git_host_name=git_host_name,
                                git_host_id=git_host_id, git_host_url=git_host_url)
        else:
            raise j.exceptions.Input(message="cannot find object  %s from git_host_id:%s" %
                                     (modelCollection.objType, git_host_id), level=1, source="", tags="", msgpub="")
    else:
        modelActive = modelCollection.get(key.decode())
    return modelActive
