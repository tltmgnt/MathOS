"""Phase XXXIII: hardened compressed-checkpoint candidate and release gates."""
import sqlite3
from pathlib import Path
import mra_x_archive as a
import mra_x_dense as dense
import mra_x_kernel as k
import mra_x_routed as r


class Store(dense.Compressed):
    """Reject incompatible database schemas; preserve verified compressed format."""
    def __init__(self,path,domains=None,budget=1000000):
        path=Path(path)
        if domains is None: a.require(path.is_file())
        super().__init__(path,domains,budget)

    def schema(self,db):
        names={x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        a.require(names in (set(),{'dense_versions'}))
        super().schema(db)
        cols=db.execute('PRAGMA table_info(dense_versions)').fetchall()
        a.require([(x[1],x[2],x[5]) for x in cols]==[('version','INTEGER',1),('hash','TEXT',0),('manifest','BLOB',0),('reads','INTEGER',0)])

    def load(self,db,row):
        snap,doc=super().load(db,row)
        a.require(len(a.canonical(snap))<=k.MAX_BYTES)
        return snap,doc


def decide(geo,worst,physical_ratio,controls_ok):
    """Review only; never automatically deploy."""
    return 'REVIEW_CANDIDATE' if controls_ok and max(geo.values())<=.9 and max(worst.values())<=1.2 and physical_ratio<=.5 else 'NO_PROMOTION'
