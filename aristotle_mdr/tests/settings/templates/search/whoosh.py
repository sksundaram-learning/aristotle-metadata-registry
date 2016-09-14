import os

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'aristotle_mdr.contrib.search_backends.whoosh.FixedWhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}
