"""Phase XLV: bounded exact-byte verified receipt reuse (trusted local process)."""
import json
from collections import OrderedDict
import mra_x_boundproof as p
import mra_x_kernel as k
import mra_x_proofguard as guard

CHECKERS={'elimination':k.check,'partition':p.check}
MAX_BYTES=min(p.MAX_BYTES,k.MAX_BYTES)


def admission(kind,raw,expected):
    guard.anchor(expected)
    p.require(type(kind) is str and kind in CHECKERS)
    p.require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES)


def check(kind,raw,expected):
    """Wire baseline: canonical JSON only, independent checker, mandatory anchor."""
    admission(kind,raw,expected)
    doc=json.loads(raw,object_pairs_hook=p.unique)
    p.require(p.canonical(doc)==raw)
    return CHECKERS[kind](doc,expected)


class Cache:
    """Private process-local receipts. No import, persistence, or thread-safety claim.

    Keys contain exact immutable bytes, format and independently trusted anchor.
    Python dict hash collisions are resolved by full key equality. Values contain
    only scalar receipt fields; returned dictionaries are detached. Bounds cover
    entry count and payload bytes, not total Python heap or verification workspace.
    """
    def __init__(self,*,entries=16,payload_bytes=524288):
        p.require(type(entries) is int and 1<=entries<=1024)
        p.require(type(payload_bytes) is int and 1<=payload_bytes<=64000000)
        self._limit=entries; self._bytes_limit=payload_bytes
        self._items=OrderedDict(); self._bytes=0
        self._hits=self._checks=self._evictions=self._bypasses=0

    def verify(self,kind,raw,expected):
        admission(kind,raw,expected)
        key=kind,expected,raw
        if key in self._items:
            receipt=self._items[key]; self._items.move_to_end(key); self._hits+=1
            return dict(receipt)
        # No cache state changes until the full independent check succeeds.
        receipt=check(kind,raw,expected); self._checks+=1
        if len(raw)>self._bytes_limit:
            self._bypasses+=1; return receipt
        while len(self._items)>=self._limit or self._bytes+len(raw)>self._bytes_limit:
            prior,_=self._items.popitem(last=False); self._bytes-=len(prior[2]); self._evictions+=1
        self._items[key]=tuple(receipt.items()); self._bytes+=len(raw)
        return dict(receipt)

    def stats(self):
        return dict(hits=self._hits,checks=self._checks,evictions=self._evictions,bypasses=self._bypasses,entries=len(self._items),payload_bytes=self._bytes)

    def clear(self):
        self._items.clear(); self._bytes=0
