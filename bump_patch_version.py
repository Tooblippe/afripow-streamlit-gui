import re


def bump_patch_version(filename="version.py"):
    # Read the file content
    with open(filename, "r") as f:
        content = f.read()

    # Regex pattern to match __version__ = "X.Y.Z"
    pattern = r'(__version__\s*=\s*")(\d+\.\d+\.\d+)(")'

    match = re.search(pattern, content)
    if not match:
        print("No version line found in", filename)
        return

    version_str = match.group(2)  # e.g., "25.1.1"
    major, minor, patch = version_str.split(".")

    # Increment the minor version
    patch = str(int(patch) + 1)

    # Build the new version string
    new_version_str = f"{major}.{minor}.{patch}"

    # Replace old version with new version in the file content
    new_content = re.sub(pattern, f'__version__ = "{new_version_str}"', content)

    # Write the updated content back to the file
    with open(filename, "w") as f:
        f.write(new_content)

    print(f"Updated version from {version_str} to {new_version_str} in {filename}")


if __name__ == "__main__":
    bump_patch_version()
