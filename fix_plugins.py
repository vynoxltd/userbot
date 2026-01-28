import os
import re

PLUGINS_DIR = "plugins"

# regex to catch filters.command(...)
COMMAND_REGEX = re.compile(
    r'@Client\.on_message\((.*?)filters\.command\((.*?)\)(.*?)\)',
    re.DOTALL
)

def fix_decorator(match):
    before = match.group(1)
    command_part = match.group(2)
    after = match.group(3)

    # extract command name
    # handles: "id", "."  OR  "id", prefixes="."
    cmd_match = re.search(r'"([^"]+)"', command_part)
    if not cmd_match:
        return match.group(0)

    cmd = cmd_match.group(1)

    return (
        '@Client.on_message('
        'filters.me & owner_only & '
        f'filters.command("{cmd}", ".")'
        ')'
    )

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "filters.command" not in content:
        return False

    new_content = COMMAND_REGEX.sub(fix_decorator, content)

    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True

    return False


def main():
    fixed = 0

    for root, _, files in os.walk(PLUGINS_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)
            if process_file(path):
                print(f"✅ Fixed: {path}")
                fixed += 1

    print(f"\n🎉 DONE — {fixed} plugin(s) fixed")

if __name__ == "__main__":
    main()
