# Benchmarks

Scripts in this folder are intended to be used to validate performance of implementations.

## Cached Property
The ``cached_property.py`` benchmark compares the ``common.decorators`` implementation of ``cached_property`` with
the standard library implementation as well as the one included with ``boltons``.

To run the benchmark from the ``observability`` project root, first make sure you've activated your virtual environment,
then follow these steps.

Install benchmarking requirements:
```bash
$ python -m pip install -r benchmark/requirements.txt
```

Run the benchmark
```bash
$ python benchmark/cached_property.py
```
