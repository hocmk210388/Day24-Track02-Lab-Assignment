"""Fallback secret scanner (replaces trufflehog on Windows)."""
import re
import os
import datetime

PATTERNS = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Password Assignment": r"password\s*=\s*[\"'][^\"']+[\"']",
    "Secret Key Assignment": r"secret_key\s*=\s*[\"'][^\"']+[\"']",
    "Private Key": r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
    "CCCD in Code": r"CCCD[:\s]+\d{12}",
}

SCAN_DIRS = ["src", "tests", "scripts"]

findings = []
for d in SCAN_DIRS:
    if not os.path.isdir(d):
        continue
    for root, _, files in os.walk(d):
        for fname in files:
            if fname.endswith(".py"):
                path = os.path.join(root, fname)
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                for name, pat in PATTERNS.items():
                    matches = re.findall(pat, content)
                    if matches:
                        findings.append({
                            "file": path,
                            "pattern": name,
                            "count": len(matches),
                        })

now = datetime.datetime.now().isoformat()
status = "CLEAN" if not findings else "SECRETS_FOUND"

with open("reports/trufflehog_report.txt", "w", encoding="utf-8") as f:
    f.write("=== TruffleHog / Secret Scan Report ===\n")
    f.write(f"Date: {now}\n")
    f.write(f"Status: {status}\n")
    f.write(f"Total findings: {len(findings)}\n\n")
    if findings:
        for item in findings:
            f.write(f"  [{item['pattern']}] in {item['file']} ({item['count']} match(es))\n")
    else:
        f.write("No secrets or credentials detected in source code.\n")
    f.write("\nNote: trufflehog Python package has PermissionError on Windows.\n")
    f.write("Used manual regex-based secret scan as fallback.\n")

print(f"Status: {status}")
print(f"Findings: {len(findings)}")
print("Report saved to reports/trufflehog_report.txt")
