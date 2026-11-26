"""Phase XL: explicit execution profiles and verified proof export.

Trusted local sequential Python API; not a sandbox or network service.
No automatic deployment or runtime-learning policy.
"""
import copy
import io
from pathlib import Path
import mra_x_archive as a
import mra_x_fork as fast
import mra_x_owned as owned
import mra_x_storage as storage
import mra_x_state as state
import mra_x_kernel as kernel

PROFILES={'performance':fast.Store,'protected':owned.Store}

class System:
    def __init__(self,path,domains=None,*,profile='protected',budget=1000000):
        a.require(type(profile) is str and profile in PROFILES)
        path=Path(path)
        if domains is None: a.require(path.is_file())
        self._profile=profile
        self._store=PROFILES[profile](path,domains,budget)

    @property
    def profile(self): return self._profile

    @property
    def version(self): return self._store.version

    def apply(self,edits,domain_edits=None,*,expected_version=None):
        a.require(type(edits) is dict and (domain_edits is None or type(domain_edits) is dict))
        if expected_version is not None:
            a.require(type(expected_version) is int and expected_version>=0)
            if expected_version!=self.version: raise state.StaleState('unexpected local version')
        r=self._store.apply(edits,domain_edits)
        return dict(version=r['version'],profile=self.profile,action=r['action'],actual=r['actual'],receipt=dict(r['receipt']))

    def get(self,version): return dict(self._store.get(version))

    def certificate(self,version):
        a.require(type(version) is int and version>=0)
        versions,docs,_=self._store.history(); a.require(version in versions)
        doc=docs[versions.index(version)]; kernel.check(doc)
        return copy.deepcopy(doc)

    def export(self,*,kind='auto',anticipated_reads=12):
        a.require(type(anticipated_reads) is int and 0<=anticipated_reads<=10000)
        a.require(type(kind) is str and (kind=='auto' or kind in storage.FORMATS))
        versions,docs,demand=self._store.history()
        if kind=='auto': (data,manifest),candidates=storage.select(versions,docs,demand,anticipated_reads)
        else: data,manifest=storage.package(versions,docs,kind); candidates=[]
        return dict(payload=data,manifest=manifest,anchor=a.digest(manifest),candidates=candidates)


def retrieve(package,version,expected_anchor):
    """Caller must preserve an independently trusted expected manifest digest."""
    return storage.retrieve(io.BytesIO(package['payload']),package['manifest'],expected_anchor,version)
