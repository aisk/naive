# Naive Template Engine

## Introduce

Naive is a too young too simple template engine.Naive compile the template source file into Python VM bytecode **directly**.

## Grammar

Naive's grammer is mostly like Django's template engine.

    from naive.compiler import Compiler
    s = "Hello, My name is {{name}}, and I'm a {% if is_male %}boy{% else %}girl{% endif %} as you see."
    co = Compiler(s).compile()    # Actually co is a code object
    eval(co, {'name': 'Asaka', 'is_male': True})

