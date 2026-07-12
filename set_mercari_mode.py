import argparse
from pathlib import Path


ENV_PATH = Path(".env")
MERCARI_KEYS = {
    "dry-run": "ENABLE_MERCARI_DRY_RUN_TASK",
    "silent": "ENABLE_MERCARI_SILENT_TASK",
    "notify": "ENABLE_MERCARI_NOTIFY_TASK",
}


def desired_values(mode):
    return {
        key: "true" if mode_name == mode else "false"
        for mode_name, key in MERCARI_KEYS.items()
    }


def read_env_lines():
    if not ENV_PATH.exists():
        return []

    return ENV_PATH.read_text(encoding="utf-8").splitlines()


def write_env_lines(lines):
    ENV_PATH.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def update_env(mode):
    values = (
        {key: "false" for key in MERCARI_KEYS.values()}
        if mode == "off"
        else desired_values(mode)
    )
    lines = read_env_lines()
    updated_keys = set()
    output_lines = []

    for line in lines:
        stripped = line.strip()
        matched_key = None

        for key in values:
            if stripped.startswith(f"{key}="):
                matched_key = key
                break

        if matched_key is None:
            output_lines.append(line)
            continue

        output_lines.append(f"{matched_key}={values[matched_key]}")
        updated_keys.add(matched_key)

    if output_lines and output_lines[-1].strip():
        output_lines.append("")

    for key, value in values.items():
        if key not in updated_keys:
            output_lines.append(f"{key}={value}")

    write_env_lines(output_lines)

    print(f"Mercari mode set to: {mode}")


def main():
    parser = argparse.ArgumentParser(
        description="Switch local Mercari task mode in .env."
    )
    parser.add_argument(
        "mode",
        choices=["off", "dry-run", "silent", "notify"],
        help="Mercari task mode to enable locally.",
    )

    args = parser.parse_args()
    update_env(args.mode)


if __name__ == "__main__":
    main()
