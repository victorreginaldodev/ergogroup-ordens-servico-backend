from contextlib import contextmanager
from threading import local


_state = local()


def get_auditoria_context():
    return getattr(_state, 'context', {})


def set_auditoria_context(**context):
    _state.context = context


def clear_auditoria_context():
    if hasattr(_state, 'context'):
        delattr(_state, 'context')


@contextmanager
def auditoria_context(**context):
    anterior = get_auditoria_context()
    set_auditoria_context(**{**anterior, **context})
    try:
        yield
    finally:
        set_auditoria_context(**anterior)
