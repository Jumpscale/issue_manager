from js9 import j
from issuemanagerlib.IndexInfo import indexinfo
from JumpScale9Lib.data.capnp.ModelBase import ModelBaseCollection
from issuemanagerlib.hostref import getFromGitHostID
from peewee import CharField, TimestampField
import peewee
import operator
from playhouse.sqlite_ext import Model

# from playhouse.sqlcipher_ext import *
# db = Database(':memory:')


class ActivityCollection(ModelBaseCollection):
    """
    This class represent a collection of users
    """

    def _getModel(self):
        class Activity(Model):
            key = CharField(index=True, default="")
            gitHostRefs = CharField(index=True, default="")
            name = CharField(index=True, default="")
            repo = CharField(index=True, default="")
            timestamp = TimestampField(index=True, default=j.data.time.epoch)

            class Meta:
                database = indexinfo.indexDB
                # order_by = ["id"]

        return Activity

    def _init(self):
        # init the index
        db = indexinfo.indexDB

        Activity = self._getModel()

        self.index = Activity

        if db.is_closed():
            db.connect()
        db.create_tables([Activity], True)

    def reset(self):
        db = indexinfo.indexDB
        db.drop_table(self._getModel())

    def add2index(self, **args):
        """
        key = CharField(index=True, default="")
        gitHostRefs = CharField(index=True, default="")
        name = CharField(index=True, default="")
        repo = CharField(index=True, default="")
        timestamp = TimestampField(index=True, default=j.data.time.epoch)


        @param args is any of the above
        """

        if "gitHostRefs" in args:
            args["gitHostRefs"] = ["%s_%s_%s" % (item["name"], item["id"], item['url']) for item in args["gitHostRefs"]]

        args = self._arraysFromArgsToString(["gitHostRefs"], args)

        # this will try to find the right index obj, if not create

        obj, isnew = self.index.get_or_create(key=args["key"])

        for key, item in args.items():
            if key in obj._data:
                # print("%s:%s" % (key, item))
                obj._data[key] = item

        obj.save()

    def getFromGitHostID(self, git_host_name, git_host_id, git_host_url, createNew=True):
        return getFromGitHostID(
            self,
            git_host_name=git_host_name,
            git_host_id=git_host_id,
            git_host_url=git_host_url,
            createNew=createNew)

    def list(self, **kwargs):
        """
        List all keys of a index


        list all entries matching kwargs. If none are specified, lists all

        e.g.
        email="reem@greenitglobe.com", name="reem"

        """
        if kwargs:
            clauses = []
            for key, val in kwargs.items():
                if not hasattr(self.index, key):
                    raise RuntimeError('%s model has no field "%s"' % (self.index._meta.name, key))
                field = (getattr(self.index, key))
                clauses.append(field.contains(val))

            res = [
                item.key for item in self.index.select().where(
                    peewee.reduce(
                        operator.and_,
                        clauses)).order_by(
                    self.index.modTime.desc())]
        else:
            res = [item.key for item in self.index.select().order_by(self.index.timestamp.desc())]

        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
        self.index.truncate_table()
