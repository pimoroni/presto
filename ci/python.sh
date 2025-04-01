# F = Pyflakes
# Q = Quotes
# E/W = pycodestyle (Whitespace, Line lengths etc)
# B - flake8-bugbear = Unused loop variables, sloppy code
# COM - flake8-commas
# BLE - flake8-blind-except
# C4  - flake8-comprehensions
# ISC - flake8-implicit-str-concat = Implicit string concat, eg: `"hello" "world"` on one line
# ICN - flake8-import-conventions = Import conventions
# PIE - flake8-pie = Misc silliness, catches range with a 0 start argument
# RET - flake8-return = Enforces straight-forward code around return statements
# SLF - flake8-self
# ARG - flake8-unused-arguments

QA_INCLUDE="F,Q,W,E,B,COM,BLE,C4,ISC,ICN,PIE,RSE,RET,SLF,ARG"
QA_IGNORE="E501,E402,COM812"

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
