
from js9 import j

from JumpScale9Lib.data.capnp.ModelBase import ModelBase


class RepoModel(ModelBase):
    """
    Model Class for a repo object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def gitHostRefSet(self, name, id, url):
        return gitHostRefSet(self, name, id, url)

    def gitHostRefExists(self, name, url):
        return gitHostRefExists(self, name, url)
