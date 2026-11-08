"""Safety filter for release notes: drops lines that could leak secrets or internals. Reads stdin, writes stdout."""
import re
import sys

BAD = re.compile(r"(?i)(secret|token|password|passwd|api[_-]?key|keystore|\.jks|\.env\b|signing|private[_ -]key|"
                 r"ghp_[A-Za-z0-9]{20,}|github_pat_|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
                 r"/home/|/Users/|C:\\\\|/data/data/|\b\d{1,3}(\.\d{1,3}){3}\b)")
for line in sys.stdin:
    if not BAD.search(line):
        sys.stdout.write(line)
