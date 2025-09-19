class WorkflowExclusion:
    paths = [
        "root['linkages']",
        "root['workflow']['id']",
        "root['workflow']['version']"
    ]

    regex_paths = [
        r".\[\d+\].\[\'id\'\]"
    ]