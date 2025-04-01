QA_INCLUDE="F,Q,W,E,B"
QA_IGNORE="E501,E402"

function qa_prepare_all {
    pip install ruff
}

function qa_examples_check {
    ruff check --select "$QA_INCLUDE" examples/ --ignore "$QA_IGNORE"
}

function qa_examples_fix {
    ruff check --select "$QA_INCLUDE" examples/ --ignore "$QA_IGNORE" --fix
}

function qa_modules_check {
    ruff check --select "$QA_INCLUDE" examples/ --ignore "$QA_IGNORE"
}

function qa_modules_fix {
    ruff check --select "$QA_INCLUDE" examples/ --ignore "$QA_IGNORE" --fix
}
