function qa_prepare_all {
    pip install ruff
}

function qa_examples_lint {
    ruff check --select F,Q,W,E examples/ --ignore E501,E402
}

function qa_examples_fix {
    ruff check --select F,Q,W,E examples/ --ignore E501,E402 --fix
}

function qa_modules_lint {
    ruff check --select F,Q,W,E examples/ --ignore E501,E402
}

function qa_modules_fix {
    ruff check --select F,Q,W,E examples/ --ignore E501,E402 --fix
}
