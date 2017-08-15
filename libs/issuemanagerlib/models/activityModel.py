
from js9 import j
from issuemanagerlib.hostref import gitHostRefSet, gitHostRefExists, gitHostRefGet
from JumpScale9Lib.data.capnp.ModelBase import ModelBase


class ActivityModel(ModelBase):
    """
    Model Class for an Activity object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def _pre_save(self):
        pass

    def gitHostRefSet(self, name, id):
        return gitHostRefSet(self, name, id)

    def gitHostRefExists(self, name):
        return gitHostRefExists(self, name)

    def gitHostRefGet(self, name):
        return gitHostRefGet(self, name)
