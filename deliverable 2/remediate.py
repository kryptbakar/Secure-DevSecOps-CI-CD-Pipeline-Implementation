# remediate.py — auto-updates vulnerable dependencies found by pip-audit.
import json
import subprocess
import sys


def run(cmd: list[str]) -> str | None:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return None


def update_requirements(package: str, fixed_version: str) -> bool:
    """Rewrite requirements.txt, bumping `package` to `fixed_version`."""
    print(f"  Updating {package} → {fixed_version} …")
    try:
        with open("requirements.txt") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("requirements.txt not found", file=sys.stderr)
        return False

    new_lines = []
    updated = False
    for line in lines:
        stripped = line.strip()
        # Match the package name (case-insensitive, ignore extras/comments)
        pkg_name = (
            stripped.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0].strip()
        )
        if pkg_name.lower() == package.lower():
            if "==" in stripped:
                new_lines.append(f"{package}=={fixed_version}\n")
            else:
                new_lines.append(f"{package}>={fixed_version}\n")
            updated = True
        else:
            new_lines.append(line)

    if updated:
        with open("requirements.txt", "w") as f:
            f.writelines(new_lines)
    else:
        print(f"  Package '{package}' not found in requirements.txt", file=sys.stderr)

    return updated


def main() -> None:
    print("=" * 60)
    print("Auto-remediation: scanning for vulnerable dependencies …")
    print("=" * 60)

    result = subprocess.run(
        ["pip-audit", "-r", "requirements.txt", "--format", "json"],
        capture_output=True,
        text=True,
    )
    audit_output = result.stdout

    if not audit_output.strip():
        print("No output from pip-audit. Nothing to do.")
        sys.exit(0)

    try:
        report = json.loads(audit_output)
    except json.JSONDecodeError:
        print("Could not parse pip-audit JSON output.", file=sys.stderr)
        print("Raw output:", audit_output, file=sys.stderr)
        sys.exit(1)

    # pip-audit JSON format: list of dicts with keys: name, version, vulns
    # Each vuln has: id, fix_versions (list)
    vulnerabilities = []
    for entry in report if isinstance(report, list) else report.get("dependencies", []):
        vulns = entry.get("vulns", [])
        if not vulns:
            continue
        name = entry.get("name", "")
        for vuln in vulns:
            fix_versions = vuln.get("fix_versions", [])
            if fix_versions:
                vulnerabilities.append(
                    {
                        "name": name,
                        "id": vuln.get("id", ""),
                        "fixed_version": fix_versions[0],
                    }
                )

    if not vulnerabilities:
        print("No actionable vulnerabilities found.")
        return

    print(f"\nFound {len(vulnerabilities)} vulnerability/ies to fix:\n")
    fixed = []
    for v in vulnerabilities:
        print(f"  [{v['id']}] {v['name']}")
        if update_requirements(v["name"], v["fixed_version"]):
            fixed.append(f"{v['name']}>={v['fixed_version']}")

    if not fixed:
        print("\nNo packages were updated in requirements.txt.")
        sys.exit(1)

    print("\nRemediation summary:")
    for pkg in fixed:
        print(f"  ✓ {pkg}")

    print("\nAuto-remediation complete. Review requirements.txt before merging.")


if __name__ == "__main__":
    main()
