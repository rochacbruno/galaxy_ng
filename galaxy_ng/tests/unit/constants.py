TEST_COLLECTION_CONFIGS = [
    {"name": "a", "namespace": "test", "dependencies": {"test.b": "*"}},
    {"name": "b", "namespace": "test", "dependencies": {"test.c": "*"}},
    {"name": "c", "namespace": "test", "dependencies": {"test.d": "*"}},
    {"name": "d", "namespace": "test"},
    {"name": "e", "namespace": "test", "dependencies": {"test.f": "*", "test.g": "*"}},
    {"name": "f", "namespace": "test", "dependencies": {"test.h": "<=3.0.0"}},
    {"name": "g", "namespace": "test", "dependencies": {"test.d": "*"}},
    {"name": "h", "namespace": "test", "version": "1.0.0"},
    {"name": "h", "namespace": "test", "version": "2.0.0"},
    {"name": "h", "namespace": "test", "version": "3.0.0"},
    {"name": "h", "namespace": "test", "version": "4.0.0"},
    {"name": "h", "namespace": "test", "version": "5.0.0"},
]
