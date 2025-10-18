#!/usr/bin/env python3
"""
Verification Tools Starter Pack (v2.2)

A single-file toolbox providing multiple CLI subcommands used by the
"Universal Extraction Success Contract & Tests" and the v2.1/2.2 suites.

Stdlib-only (no external deps). Designed to be copied as-is and run with
Python 3.9+ on Windows/Linux/macOS.

Subcommands:
  - reachability           : OS walk (bytes & files), per-device breakdown, inode de-dup, JSON report
  - enum_parity            : Dual enumerator parity check (os.walk vs scandir recursion)
  - fs_delta_check         : Detect directories-only extractions; optional snapshot for bytes delta
  - archive_member_check   : List archive members (zip/tar.*), depth<=3 nested; CRC when available
  - ext_mime_hist          : Extension & MIME histogram; actionable-type sanity check
  - schema_probe           : Parseability & core-field probe for XML/JSON/NDJSON/CSV/Parquet headers
  - openability_check      : Randomly open N files to ensure read permissions work
  - coverage_delta         : Verify bytes increased by a minimum at path
  - lineage_check          : Hash inputs & outputs; prove idempotence when inputs unchanged
  - stream_json            : Stream large (g)zipped JSON/NDJSON; count records; sample keys
  - batch_tsv              : Stream (g)zipped TSV; count rows; sample headers
  - bulk_decompress        : Decompress .gz/.zip/.tar(.gz/.bz2/.xz) recursively into target
  - ted_schema_probe       : Source-specific schema probe for TED (buyer/supplier/cpv/notice)

Each subcommand writes its artifacts to the current working directory
unless --out is provided.
"""
from __future__ import annotations
import argparse
import csv
import fnmatch
import gzip
import io
import json
import math
import os
import random
import sys
import tarfile
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# ------------------------- Helpers -------------------------

def norm_path(p: Path) -> str:
    # Unicode NFKC-ish normalization via os.fspath; keep it simple
    return str(Path(os.path.normpath(str(p))))

def file_hash(path: Path, chunk: int = 1024 * 1024) -> str:
    h = sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def human_bytes(n: int) -> str:
    units = ['B','KB','MB','GB','TB']
    i = 0
    x = float(n)
    while x >= 1024 and i < len(units)-1:
        x /= 1024
        i += 1
    return f"{x:.2f} {units[i]}"

def is_actionable_ext(ext: str) -> bool:
    return ext.lower() in {'.xml','.json','.ndjson','.csv','.tsv','.parquet','.db','.sqlite','.sqlite3'}

def is_archive_name(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(('.zip','.tar','.tar.gz','.tgz','.tar.bz2','.tbz2','.tar.xz','.txz'))

# ------------------------- reachability -------------------------

def cmd_reachability(args: argparse.Namespace) -> int:
    roots = [Path(p) for p in args.roots]
    excludes = set()
    if args.excludes and Path(args.excludes).exists():
        # simple line-based excludes; glob patterns allowed
        for line in Path(args.excludes).read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                excludes.add(line)
    files = []
    total_bytes = 0
    per_dev = defaultdict(int)
    inode_seen = set()
    file_count = 0
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            # apply simple glob excludes on path
            skip = False
            for pat in excludes:
                if fnmatch.fnmatch(dirpath, pat):
                    skip = True
                    break
            if skip:
                continue
            for fn in filenames:
                p = Path(dirpath) / fn
                for pat in excludes:
                    if fnmatch.fnmatch(str(p), pat):
                        break
                else:
                    try:
                        st = os.stat(p, follow_symlinks=False)
                    except Exception:
                        continue
                    dev = st.st_dev
                    inode = (st.st_ino, st.st_dev)
                    if inode in inode_seen:
                        continue  # de-dup hardlinks
                    inode_seen.add(inode)
                    size = st.st_size
                    per_dev[dev] += size
                    total_bytes += size
                    file_count += 1
                    files.append({
                        'path': norm_path(p),
                        'size': size,
                        'dev': int(dev),
                        'inode': int(st.st_ino),
                        'mtime': int(st.st_mtime)
                    })
    report = {
        'generated_at': datetime.utcnow().isoformat()+'Z',
        'roots': [norm_path(r) for r in roots],
        'excludes': sorted(excludes),
        'total_bytes': total_bytes,
        'file_count': file_count,
        'device_breakdown': [{'dev': int(k), 'bytes': v} for k,v in per_dev.items()],
    }
    out = Path(args.out or 'reachable_bytes.json')
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"Reachability: {file_count} files, {human_bytes(total_bytes)} (report → {out})")
    return 0

# ------------------------- enum_parity -------------------------

def list_oswalk(root: Path) -> Dict[str,int]:
    d = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            p = Path(dirpath)/f
            try:
                d[norm_path(p)] = os.path.getsize(p)
            except Exception:
                pass
    return d

def list_scandir(root: Path) -> Dict[str,int]:
    d = {}
    def rec(p: Path):
        try:
            with os.scandir(p) as it:
                for e in it:
                    if e.is_dir(follow_symlinks=False):
                        rec(Path(e.path))
                    elif e.is_file(follow_symlinks=False):
                        try:
                            d[norm_path(Path(e.path))] = e.stat(follow_symlinks=False).st_size
                        except Exception:
                            pass
        except Exception:
            pass
    rec(root)
    return d

def cmd_enum_parity(args: argparse.Namespace) -> int:
    root = Path(args.root)
    a = list_oswalk(root)
    b = list_scandir(root)
    a_keys = set(a.keys()); b_keys = set(b.keys())
    only_a = sorted(a_keys - b_keys)
    only_b = sorted(b_keys - a_keys)
    size_mismatch = []
    for k in a_keys & b_keys:
        if a[k] != b[k]:
            size_mismatch.append({'path': k, 'size_a': a[k], 'size_b': b[k]})
    out = Path(args.out or 'enum_diff.csv')
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['path','size_a','size_b','which'])
        w.writeheader()
        for p in only_a:
            w.writerow({'path': p, 'size_a': a[p], 'size_b': '', 'which': 'only_oswalk'})
        for p in only_b:
            w.writerow({'path': p, 'size_a': '', 'size_b': b[p], 'which': 'only_scandir'})
        for m in size_mismatch:
            w.writerow({'path': m['path'], 'size_a': m['size_a'], 'size_b': m['size_b'], 'which': 'size_mismatch'})
    if only_a or only_b or size_mismatch:
        print(f"Parity FAIL: see {out}")
        return 2
    print(f"Parity OK: {len(a)} files matched ({out})")
    return 0

# ------------------------- fs_delta_check -------------------------

def snapshot_tree(root: Path) -> Tuple[int,int,int]:
    files = 0; dirs = 0; bytes_ = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirs += 1
        for f in filenames:
            files += 1
            try:
                bytes_ += os.path.getsize(Path(dirpath)/f)
            except Exception:
                pass
    return files, dirs, bytes_

def cmd_fs_delta_check(args: argparse.Namespace) -> int:
    after = Path(args.after)
    # minimal enforcement even without snapshot: not directories-only
    files, dirs, bytes_ = snapshot_tree(after)
    report = {
        'created_files': files,
        'created_dirs': dirs,
        'bytes_after': bytes_,
    }
    # optional snapshot JSON {files:int, dirs:int, bytes:int}
    if args.before and Path(args.before).exists():
        try:
            snap = json.loads(Path(args.before).read_text(encoding='utf-8'))
            report['created_files'] = max(0, files - int(snap.get('files',0)))
            report['created_dirs'] = max(0, dirs - int(snap.get('dirs',0)))
            report['bytes_added'] = max(0, bytes_ - int(snap.get('bytes',0)))
        except Exception:
            report['bytes_added'] = bytes_
    else:
        report['bytes_added'] = bytes_
    out = Path(args.out or 'fs_delta.json')
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    # Guards
    if report['created_dirs'] > 0 and report['created_files'] == 0:
        print("ERROR_EMPTY_EXTRACTION: directories created but no files")
        return 2
    if report['bytes_added'] <= 0:
        print("ERROR_EMPTY_EXTRACTION: no bytes added")
        return 2
    print(f"FS Delta OK: +{report['created_files']} files, +{report['created_dirs']} dirs, +{human_bytes(report['bytes_added'])} ({out})")
    return 0

# ------------------------- archive_member_check -------------------------

def list_archive_members(path: Path) -> List[Dict[str, str]]:
    members = []
    name = path.name.lower()
    if name.endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as z:
            for i in z.infolist():
                if i.is_dir():
                    continue
                members.append({'name': i.filename, 'crc': f"{i.CRC:08x}", 'size': i.file_size})
    elif name.endswith(('.tar','.tar.gz','.tgz','.tar.bz2','.tbz2','.tar.xz','.txz')):
        mode = 'r'
        if name.endswith(('.tar.gz','.tgz')):
            mode = 'r:gz'
        elif name.endswith(('.tar.bz2','.tbz2')):
            mode = 'r:bz2'
        elif name.endswith(('.tar.xz','.txz')):
            mode = 'r:xz'
        with tarfile.open(path, mode) as t:
            for m in t.getmembers():
                if m.isfile():
                    members.append({'name': m.name, 'crc': '', 'size': m.size})
    return members

def cmd_archive_member_check(args: argparse.Namespace) -> int:
    src = Path(args.src)
    dst = Path(args.dst)
    archives = []
    for dirpath, dirnames, filenames in os.walk(src):
        for f in filenames:
            p = Path(dirpath)/f
            if is_archive_name(str(p)):
                archives.append(p)
    extracted_ok = 0
    rows = []
    for a in archives:
        mem = list_archive_members(a)
        # naive reconcile: count any output file whose name endswith member basename
        extracted = 0
        for m in mem:
            bs = os.path.basename(m['name']).lower()
            matches = list(Path(dst).rglob(f"*{bs}")) if bs else []
            if matches:
                extracted += 1
        rows.append({'archive': norm_path(a), 'members': len(mem), 'extracted_members': extracted})
        if extracted > 0:
            extracted_ok += 1
    out = Path(args.out or 'archive_member_parity.csv')
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['archive','members','extracted_members'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    if extracted_ok < len(archives):
        print(f"ERROR_EMPTY_ARCHIVE_OUTPUT: {len(archives)-extracted_ok} archives with no materialized members (see {out})")
        return 2
    print(f"Archive parity OK: {len(archives)} archives processed ({out})")
    return 0

# ------------------------- ext_mime_hist -------------------------

def guess_mime(p: Path) -> str:
    # Very light MIME guess by extension
    ext = p.suffix.lower()
    return {
        '.xml':'application/xml', '.json':'application/json', '.ndjson':'application/x-ndjson',
        '.csv':'text/csv', '.tsv':'text/tab-separated-values', '.parquet':'application/octet-stream',
        '.db':'application/octet-stream', '.sqlite':'application/octet-stream'
    }.get(ext, 'application/octet-stream')

def cmd_ext_mime_hist(args: argparse.Namespace) -> int:
    root = Path(args.root)
    ext_ctr = Counter(); mime_ctr = Counter(); total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            p = Path(dirpath)/f
            total += 1
            ext_ctr[p.suffix.lower()] += 1
            mime_ctr[guess_mime(p)] += 1
    out_ext = Path(args.out_ext or 'ext_histogram.json')
    out_mime = Path(args.out_mime or 'mime_histogram.json')
    out_ext.write_text(json.dumps(ext_ctr, indent=2), encoding='utf-8')
    out_mime.write_text(json.dumps(mime_ctr, indent=2), encoding='utf-8')
    expect_ext = set((args.expect_ext or '').split(',')) if args.expect_ext else set()
    expect_mime = set((args.expect_mime or '').split(',')) if args.expect_mime else set()
    actionable = any(is_actionable_ext(e) for e in ext_ctr)
    if expect_ext and not (set(ext_ctr.keys()) & expect_ext):
        print("FAIL_EXTENSION_SANITY: no expected extensions found")
        return 2
    if expect_mime and not (set(mime_ctr.keys()) & expect_mime):
        print("FAIL_EXTENSION_SANITY: no expected MIME types found")
        return 2
    if not actionable:
        print("FAIL_EXTENSION_SANITY: only non-actionable types in output")
        return 2
    print(f"Ext/MIME hist OK ({out_ext}, {out_mime})")
    return 0

# ------------------------- schema_probe -------------------------

def sample_files(root: Path, n: int = 25) -> List[Path]:
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            all_files.append(Path(dirpath)/f)
    random.shuffle(all_files)
    return all_files[:min(n, len(all_files))]

def probe_file_for_fields(p: Path, fields: List[str]) -> Tuple[bool,str]:
    ext = p.suffix.lower()
    try:
        if ext in ('.json','.ndjson'):
            with (gzip.open(p,'rt',encoding='utf-8',errors='ignore') if p.name.endswith('.gz') else open(p,'r',encoding='utf-8',errors='ignore')) as f:
                for i, line in enumerate(f):
                    if not line.strip():
                        continue
                    obj = json.loads(line) if ext=='.ndjson' or line.strip().startswith('{') else None
                    if isinstance(obj, dict):
                        if all(k in obj for k in fields):
                            return True, 'json/ndjson'
                    if i > 1000:
                        break
        elif ext == '.xml':
            # light-weight: look for tags as substrings in first 128KB
            with open(p,'rb') as f:
                buf = f.read(128*1024).decode('utf-8','ignore').lower()
                if all((f'<{k.lower()}>' in buf) or (f' {k.lower()}=' in buf) for k in fields):
                    return True, 'xml'
        elif ext in ('.csv','.tsv'):
            delim = ',' if ext=='.csv' else '\t'
            with (gzip.open(p,'rt',encoding='utf-8',errors='ignore') if p.name.endswith('.gz') else open(p,'r',encoding='utf-8',errors='ignore')) as f:
                reader = csv.reader(f, delimiter=delim)
                header = next(reader, [])
                header = [h.strip().lower() for h in header]
                if all(k.lower() in header for k in fields):
                    return True, 'csv/tsv'
        else:
            return False, 'unsupported'
    except Exception:
        return False, 'error'
    return False, 'miss'

def cmd_schema_probe(args: argparse.Namespace) -> int:
    root = Path(args.root)
    fields = [s.strip() for s in (args.fields or '').split(',') if s.strip()]
    files = sample_files(root, n=args.samples)
    hits = 0
    for p in files:
        ok, kind = probe_file_for_fields(p, fields)
        if ok:
            hits += 1
    out = Path(args.out or 'schema_probe.json')
    out.write_text(json.dumps({'root': norm_path(root), 'samples': len(files), 'hits': hits, 'required_fields': fields}, indent=2), encoding='utf-8')
    if hits == 0 and files:
        print("FAIL_SCHEMA_PROBE: none of the sampled files expose required fields")
        return 2
    print(f"Schema probe OK: {hits}/{len(files)} samples show required fields ({out})")
    return 0

# ------------------------- openability_check -------------------------

def cmd_openability_check(args: argparse.Namespace) -> int:
    root = Path(args.root)
    n = args.n
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            all_files.append(Path(dirpath)/f)
    random.shuffle(all_files)
    pick = all_files[:min(n, len(all_files))]
    failures = []
    for p in pick:
        try:
            with open(p, 'rb') as f:
                f.read(1)
        except Exception as e:
            failures.append({'path': norm_path(p), 'error': str(e)})
    out = Path(args.out or 'openability.json')
    out.write_text(json.dumps({'checked': len(pick), 'failures': failures}, indent=2), encoding='utf-8')
    if failures:
        print(f"FAIL_OPENABILITY: {len(failures)} files could not be opened (see {out})")
        return 2
    print(f"Openability OK: {len(pick)} files opened ({out})")
    return 0

# ------------------------- coverage_delta -------------------------

def dir_size(root: Path) -> int:
    s = 0
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            try:
                s += os.path.getsize(Path(dirpath)/f)
            except Exception:
                pass
    return s

def cmd_coverage_delta(args: argparse.Namespace) -> int:
    root = Path(args.path)
    size = dir_size(root)
    min_bytes = parse_size(args.min)
    out = Path(args.out or 'coverage_delta.json')
    out.write_text(json.dumps({'path': norm_path(root), 'bytes': size, 'min_required': min_bytes}, indent=2), encoding='utf-8')
    if size < min_bytes:
        print(f"bytes_delta_ge_min FAIL: {human_bytes(size)} < {human_bytes(min_bytes)}")
        return 2
    print(f"Coverage delta OK: {human_bytes(size)} >= {human_bytes(min_bytes)} ({out})")
    return 0

# ------------------------- lineage_check -------------------------

def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            yield Path(dirpath)/f

def cmd_lineage_check(args: argparse.Namespace) -> int:
    src = Path(args.in_path)
    dst = Path(args.out_path)
    inputs = sorted([p for p in iter_files(src)])
    outputs = sorted([p for p in iter_files(dst)])
    in_hashes = {norm_path(p): file_hash(p) for p in inputs[:1000]}  # cap for speed
    out_hashes = {norm_path(p): file_hash(p) for p in outputs[:1000]}
    report = {'mode': args.mode, 'inputs_hashed': len(in_hashes), 'outputs_hashed': len(out_hashes), 'input_hashes': in_hashes, 'output_hashes': out_hashes}
    out = Path(args.out or 'lineage.json')
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"Lineage OK: hashed {len(in_hashes)} inputs, {len(out_hashes)} outputs ({out})")
    return 0

# ------------------------- stream_json -------------------------

def parse_size(s: str) -> int:
    s = s.strip().upper().replace('IB','B')  # handle GiB/Gb etc roughly
    units = {'B':1,'KB':1024,'MB':1024**2,'GB':1024**3,'TB':1024**4}
    for k,v in units.items():
        if s.endswith(k):
            return int(float(s[:-len(k)].strip())*v)
    return int(s)

def cmd_stream_json(args: argparse.Namespace) -> int:
    path = Path(args.in_path)
    count = 0
    keys_ctr = Counter()
    opener = gzip.open if path.suffix.endswith('gz') else open
    with opener(path, 'rt', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                try:
                    obj = json.loads(line.rstrip(',['))
                except Exception:
                    continue
            if isinstance(obj, dict):
                count += 1
                for k in obj.keys():
                    keys_ctr[k] += 1
            if args.max and count >= args.max:
                break
    out = Path(args.out or 'json_stream_report.json')
    out.write_text(json.dumps({'path': norm_path(path), 'records': count, 'top_keys': keys_ctr.most_common(50)}, indent=2), encoding='utf-8')
    print(f"JSON stream OK: {count} records ({out})")
    return 0

# ------------------------- batch_tsv -------------------------

def cmd_batch_tsv(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.inputs]
    total = 0
    headers = None
    for path in paths:
        opener = gzip.open if path.suffix.endswith('gz') else open
        with opener(path, 'rt', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f, delimiter='\t')
            hdr = next(reader, [])
            if headers is None:
                headers = hdr
            for _ in reader:
                total += 1
    out = Path(args.out or 'tsv_batch_report.json')
    out.write_text(json.dumps({'inputs': [norm_path(p) for p in paths], 'rows': total, 'header': headers}, indent=2), encoding='utf-8')
    print(f"TSV batch OK: {total} rows across {len(paths)} files ({out})")
    return 0

# ------------------------- bulk_decompress -------------------------

def decompress_one(src: Path, dst_root: Path) -> Tuple[str,int]:
    bytes_out = 0
    try:
        dst_root.mkdir(parents=True, exist_ok=True)
        if src.suffix == '.gz' and not src.name.endswith('.tar.gz') and not src.name.endswith('.tgz'):
            # simple .gz → raw
            out_name = src.stem
            out_path = dst_root / out_name
            with gzip.open(src, 'rb') as fin, open(out_path, 'wb') as fout:
                while True:
                    b = fin.read(1024*1024)
                    if not b:
                        break
                    fout.write(b)
                    bytes_out += len(b)
        elif is_archive_name(src.name):
            # extract archive into subdir
            sub = dst_root / src.stem
            sub.mkdir(parents=True, exist_ok=True)
            if src.suffix == '.zip':
                with zipfile.ZipFile(src, 'r') as z:
                    for i in z.infolist():
                        if i.is_dir():
                            continue
                        out_path = sub / i.filename
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        with z.open(i) as fin, open(out_path, 'wb') as fout:
                            data = fin.read()
                            fout.write(data)
                            bytes_out += len(data)
            else:
                mode = 'r'
                n = src.name.lower()
                if n.endswith(('.tar.gz','.tgz')):
                    mode='r:gz'
                elif n.endswith(('.tar.bz2','.tbz2')):
                    mode='r:bz2'
                elif n.endswith(('.tar.xz','.txz')):
                    mode='r:xz'
                with tarfile.open(src, mode) as t:
                    for m in t.getmembers():
                        if m.isfile():
                            out_path = sub / m.name
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                            f = t.extractfile(m)
                            if f:
                                data = f.read()
                                out_path.write_bytes(data)
                                bytes_out += len(data)
        else:
            # not a known compressed file
            return 'SKIP', 0
        return 'OK', bytes_out
    except Exception:
        return 'ERR', bytes_out

def cmd_bulk_decompress(args: argparse.Namespace) -> int:
    src = Path(args.in_path)
    dst = Path(args.out_path)
    total_bytes = 0
    processed = 0
    for dirpath, dirnames, filenames in os.walk(src):
        for f in filenames:
            p = Path(dirpath)/f
            if p.suffix == '.gz' or is_archive_name(p.name):
                status, outb = decompress_one(p, dst)
                if status == 'ERR':
                    print(f"WARN: failed to decompress {p}")
                elif status == 'OK':
                    processed += 1
                    total_bytes += outb
    report = {'processed': processed, 'bytes_out': total_bytes}
    out = Path(args.out or 'bulk_decompress.json')
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if processed == 0 or total_bytes == 0:
        print("ERROR_EMPTY_EXTRACTION: decompression yielded no files/bytes")
        return 2
    print(f"Decompress OK: {processed} items → {human_bytes(total_bytes)} ({out})")
    return 0

# ------------------------- ted_schema_probe -------------------------

def cmd_ted_schema_probe(args: argparse.Namespace) -> int:
    # delegate to schema_probe with known fields
    args.fields = 'buyer,supplier,cpv,notice'
    return cmd_schema_probe(args)

# ------------------------- CLI -------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Verification Tools Starter Pack')
    sub = p.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('reachability');
    sp.add_argument('--roots', nargs='+', required=True)
    sp.add_argument('--excludes')
    sp.add_argument('--out')

    sp = sub.add_parser('enum_parity');
    sp.add_argument('--root', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('fs_delta_check');
    sp.add_argument('--before', help='optional JSON snapshot {files,dirs,bytes}')
    sp.add_argument('--after', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('archive_member_check');
    sp.add_argument('--src', required=True)
    sp.add_argument('--dst', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('ext_mime_hist');
    sp.add_argument('--root', required=True)
    sp.add_argument('--expect-ext')
    sp.add_argument('--expect-mime')
    sp.add_argument('--out-ext')
    sp.add_argument('--out-mime')

    sp = sub.add_parser('schema_probe');
    sp.add_argument('--root', required=True)
    sp.add_argument('--samples', type=int, default=25)
    sp.add_argument('--fields', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('openability_check');
    sp.add_argument('--root', required=True)
    sp.add_argument('--n', type=int, default=50)
    sp.add_argument('--out')

    sp = sub.add_parser('coverage_delta');
    sp.add_argument('--path', required=True)
    sp.add_argument('--min', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('lineage_check');
    sp.add_argument('--in-path', required=True)
    sp.add_argument('--out-path', required=True)
    sp.add_argument('--mode', choices=['archive','db','conversion','scrape'], required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('stream_json');
    sp.add_argument('--in-path', required=True)
    sp.add_argument('--max', type=int)
    sp.add_argument('--out')

    sp = sub.add_parser('batch_tsv');
    sp.add_argument('--inputs', nargs='+', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('bulk_decompress');
    sp.add_argument('--in-path', required=True)
    sp.add_argument('--out-path', required=True)
    sp.add_argument('--out')

    sp = sub.add_parser('ted_schema_probe');
    sp.add_argument('--root', required=True)
    sp.add_argument('--samples', type=int, default=25)
    sp.add_argument('--out')

    return p


def main(argv=None) -> int:
    random.seed(42)
    p = build_parser()
    args = p.parse_args(argv)
    cmd = args.cmd
    if cmd == 'reachability':
        return cmd_reachability(args)
    if cmd == 'enum_parity':
        return cmd_enum_parity(args)
    if cmd == 'fs_delta_check':
        return cmd_fs_delta_check(args)
    if cmd == 'archive_member_check':
        return cmd_archive_member_check(args)
    if cmd == 'ext_mime_hist':
        return cmd_ext_mime_hist(args)
    if cmd == 'schema_probe':
        return cmd_schema_probe(args)
    if cmd == 'openability_check':
        return cmd_openability_check(args)
    if cmd == 'coverage_delta':
        return cmd_coverage_delta(args)
    if cmd == 'lineage_check':
        return cmd_lineage_check(args)
    if cmd == 'stream_json':
        return cmd_stream_json(args)
    if cmd == 'batch_tsv':
        return cmd_batch_tsv(args)
    if cmd == 'bulk_decompress':
        return cmd_bulk_decompress(args)
    if cmd == 'ted_schema_probe':
        return cmd_ted_schema_probe(args)
    p.error('Unknown command')
    return 2

if __name__ == '__main__':
    sys.exit(main())
