#!/usr/bin/env python3
"""
extract_k_systems.py

Search for files related to "K Systems" work and package them into a timestamped tar.gz archive,
with a manifest and SHA-256 checksum.

Usage:
    python3 extract_k_systems.py --target /home/brendon --out ./export_bundle --keywords-file keywords.txt

Notes:
 - By default searches common user folders and skips OS/system directories.
 - The script is non-destructive: it only reads and copies files to a staging directory.
 - Review EXCLUDE_DIRS and KEYWORDS below before running.
"""

import argparse
import os
import sys
import shutil
import tarfile
import hashlib
import time
import stat
from pathlib import Path
import json

# -----------------------
# CONFIGURE THESE
# -----------------------
DEFAULT_KEYWORDS = [
    "k-systems", "k-sys", "kss", "crown", "omega", "genesis", "genesisotblack",
    "genesisΩ", "kharnita", "kharNITA", "k-math", "k_math", "eido", "eido_math",
    "kpharma", "k-pharma", "sha-ark", "sha_ark", "sha_arc3", "shaark", "shakedown",
    "chronogenesis", "k-sys-gums", "k-sys-gums-2025", "crown_jewel", "crownjewel",
    "geneforge", "ether_slip", "q-hornet", "q-hornet_o", "qhornet", "ark", "Ω",
    "kharnita_compiler", "kharnita_vm", "kharnita_fra", "edenic", "edenic_rootblock",
    "ΩCOIN", "crown-usd", "crown-waves", "Ω-STATE", "k-sys-gums-2025-final",
    "k-system", "k-systems-classified", "k-sys-gums-2025-final", "k-sys-gums",
    "kss-darpa-audit", "Top Secret K-System", "K-SYS-GUMS", "ATNYCHI", "ATNYCHI0",
    "K-SYSTEM White Paper", "K-SYS-GUMS-2025-FINAL", "K-SYS-GUMS-2025-FINAL.py"
]

# File extensions to prioritize (set empty to search all)
PRIORITY_EXTS = [
    ".pdf", ".doc", ".docx", ".txt", ".md", ".py", ".ipynb",
    ".pyc", ".json", ".yml", ".yaml", ".csv", ".xlsx", ".pptx", ".zip",
    ".tar", ".tgz", ".pem", ".key", ".pub", ".sqlite", ".db"
]

# Directories to exclude by default (modify as needed)
EXCLUDE_DIRS = {
    "/proc", "/sys", "/dev", "/run", "/var/lib", "/var/run",
    "/usr", "/bin", "/sbin", "/lib", "/lib64", "/snap",
    "/Applications", "/System", "/Windows", "/Program Files", "/Program Files (x86)"
}

# Maximum file size to copy (bytes) - set to None for unlimited (careful).
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5 GiB default cap per file

# -----------------------
# Helper functions
# -----------------------
def user_confirm(prompt: str) -> bool:
    try:
        r = input(prompt + " [y/N]: ").strip().lower()
        return r == "y" or r == "yes"
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def should_exclude_path(path: Path, exclude_dirs):
    try:
        # Normalize, compare top-level
        for ex in exclude_dirs:
            if str(path).startswith(str(ex)):
                return True
    except Exception:
        pass
    return False

def copy_with_metadata(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)  # copies metadata (mtime, atime, mode bits)
    try:
        st = src.stat()
        # preserve executable bit if set
        if st.st_mode & stat.S_IXUSR:
            dst.chmod(dst.stat().st_mode | stat.S_IXUSR)
    except Exception:
        pass

# -----------------------
# Main extraction logic
# -----------------------
def extract(target_dir: Path, out_dir: Path, keywords, priority_exts, exclude_dirs, max_file_size, dry_run=False):
    target_dir = target_dir.resolve()
    out_dir = out_dir.resolve()
    staging = out_dir / "staging"
    manifest = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": str(target_dir),
        "files_copied": [],
        "total_bytes": 0,
        "total_files": 0,
        "excluded_dirs": list(exclude_dirs),
        "keywords": keywords,
        "crown_seal": None
    }

    print(f"[+] Starting scan of {target_dir}")
    print(f"[+] Staging directory: {staging}")
    if dry_run:
        print("[!] DRY RUN mode - no files will be copied.")
    if staging.exists() and any(staging.iterdir()):
        if not user_confirm(f"Staging dir {staging} already exists and is not empty. Remove contents?"):
            print("Aborting.")
            sys.exit(1)
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    # Walk the filesystem
    for root, dirs, files in os.walk(target_dir, topdown=True):
        root_path = Path(root)
        # prune excluded dirs
        dirs[:] = [d for d in dirs if not should_exclude_path(root_path / d, exclude_dirs)]
        # Also skip hidden system directories if desired (optional)
        try:
            for fname in files:
                fpath = root_path / fname
                # skip special files
                if not fpath.is_file():
                    continue
                # skip very large files
                try:
                    fsize = fpath.stat().st_size
                except Exception:
                    fsize = 0
                if max_file_size and fsize > max_file_size:
                    continue
                # heuristic match: keywords in filename or in parent folder name or extension match
                searchable = (fname + " " + root_path.name).lower()
                matched = False
                for kw in keywords:
                    if kw.lower() in searchable:
                        matched = True
                        break
                # if not matched, also check extension priority
                ext = fpath.suffix.lower()
                if (not matched) and (ext in priority_exts):
                    matched = True
                if not matched:
                    continue

                # ready to copy
                rel_path = fpath.relative_to(target_dir)
                dest = staging / rel_path
                manifest_entry = {
                    "source_path": str(fpath),
                    "relative_path": str(rel_path),
                    "size_bytes": fsize,
                    "copied_to": str(dest),
                }
                manifest["files_copied"].append(manifest_entry)
                manifest["total_bytes"] += fsize
                manifest["total_files"] += 1

                if not dry_run:
                    try:
                        copy_with_metadata(fpath, dest)
                    except Exception as e:
                        manifest_entry["error"] = str(e)
                        print(f"[!] Failed copying {fpath}: {e}")
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user. Exiting loop.")
            break

    # After copy, produce archive
    manifest_path = staging / "EXTRACTION_MANIFEST.json"
    with manifest_path.open("w", encoding="utf-8") as mf:
        mf.write(json.dumps(manifest, indent=2))
    print(f"[+] Manifest written: {manifest_path}")

    # Create crown seal placeholder
    crown_placeholder = staging / "CROWN_SEAL_PLACEHOLDER.txt"
    crown_placeholder.write_text("CROWN_SEAL: not provided\nAdd your crown seal file (image or signed token) to this folder.\n", encoding="utf-8")

    # Create tar.gz
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    archive_name = out_dir / f"k-systems-export-{ts}.tar.gz"
    print(f"[+] Creating archive: {archive_name}")
    with tarfile.open(archive_name, "w:gz") as tar:
        # add staging folder contents only, not the staging folder itself
        for item in staging.iterdir():
            tar.add(item, arcname=item.name)

    # compute checksum
    checksum = compute_sha256(archive_name)
    checksum_path = out_dir / f"{archive_name.name}.sha256"
    checksum_path.write_text(checksum + "  " + archive_name.name + "\n", encoding="utf-8")

    # write summary
    summary = {
        "archive": str(archive_name),
        "sha256": checksum,
        "manifest": str(manifest_path),
        "timestamp_utc": manifest["timestamp_utc"],
        "total_files": manifest["total_files"],
        "total_bytes": manifest["total_bytes"]
    }
    summary_path = out_dir / "EXTRACTION_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[+] Archive completed: {archive_name}")
    print(f"[+] SHA256: {checksum}")
    print(f"[+] Summary: {summary_path}")

    return summary

# -----------------------
# CLI
# -----------------------
def main():
    parser = argparse.ArgumentParser(description="Extract K-Systems related files into a package.")
    parser.add_argument("--target", "-t", default=str(Path.home()), help="Target directory to search (default: $HOME)")
    parser.add_argument("--out", "-o", default="./k-systems-export", help="Output folder for staging and archive")
    parser.add_argument("--keywords-file", "-k", default=None, help="Optional file with one keyword per line")
    parser.add_argument("--max-file-size", type=int, default=MAX_FILE_SIZE, help="Maximum file size in bytes to include (default 5GB)")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report only; do not copy files")
    parser.add_argument("--no-confirm", action="store_true", help="Do not prompt for confirmations (be careful)")
    args = parser.parse_args()

    try:
        if os.geteuid() == 0:
            print("[!] Warning: Running as root. It's safer to run as a normal user. Continue with caution.")
    except AttributeError:
        # os.geteuid() not available on Windows
        pass

    # load keywords
    keywords = DEFAULT_KEYWORDS.copy()
    if args.keywords_file:
        kf = Path(args.keywords_file)
        if kf.exists():
            kws = [l.strip() for l in kf.read_text(encoding="utf-8").splitlines() if l.strip()]
            keywords = kws + keywords  # prioritize user-supplied
        else:
            print(f"[!] keywords file {kf} not found. Using defaults.")

    target_dir = Path(args.target)
    out_dir = Path(args.out)
    if not target_dir.exists():
        print(f"[!] target {target_dir} does not exist.")
        sys.exit(1)

    # show summary and confirm
    print("-----------------------------------------------------")
    print("K-Systems Extraction Tool")
    print(f"Target: {target_dir}")
    print(f"Output: {out_dir}")
    print(f"Keywords: {len(keywords)} keywords (first 10): {keywords[:10]}")
    print(f"Exclude dirs (sample): {list(EXCLUDE_DIRS)[:5]}")
    print("Dry run:", args.dry_run)
    print("-----------------------------------------------------")
    if not args.no_confirm:
        if not user_confirm("Proceed with extraction?"):
            print("Cancelled by user.")
            sys.exit(0)

    out_dir.mkdir(parents=True, exist_ok=True)
    summary = extract(
        target_dir=target_dir,
        out_dir=out_dir,
        keywords=keywords,
        priority_exts=[e.lower() for e in PRIORITY_EXTS],
        exclude_dirs=EXCLUDE_DIRS,
        max_file_size=args.max_file_size,
        dry_run=args.dry_run
    )
    print("[+] Done. Review the summary and manifest in the output folder.")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
