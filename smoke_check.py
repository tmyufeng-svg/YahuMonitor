import py_compile


FILES_TO_COMPILE = [
    "main.py",
    "config.py",
    "config.example.py",
    "config_check.py",
    "release_check.py",
    "task_config.py",
    "task_config_check.py",
    "task_editor.py",
    "task_schema.py",
    "export_task_schema.py",
    "categories.py",
    "list_categories.py",
    "set_mercari_mode.py",
    "task_probe.py",
    "mercari_probe.py",
    "yahoo.py",
    "mercari.py",
    "database.py",
    "notifier.py",
    "browser_manager.py",
]


def main():
    for path in FILES_TO_COMPILE:
        py_compile.compile(path, doraise=True)
        print(f"Compiled: {path}")

    print("Smoke check OK")


if __name__ == "__main__":
    main()
