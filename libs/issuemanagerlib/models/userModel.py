
from js9 import j
from issuemanagerlib.hostref import *
from JumpScale9Lib.data.capnp.ModelBase import ModelBase


class UserModel(ModelBase):
    """
    Model Class for an user object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def gitHostRefSet(self, name, id):
        return gitHostRefSet(self, name, id)

    def gitHostRefExists(self, name):
        return gitHostRefExists(self, name)

    def _pre_save(self):
        pass
