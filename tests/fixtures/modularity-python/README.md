# Adopting-project boundary checker demonstration

Run `python3 check_boundaries.py` in this directory. `src/domain.py` owns amount
validation; standard-library imports are allowed, while service, adapter and
vendor SDK imports are forbidden. The production recipe for this fixture is the
same script invoked by `tests/test_modularity.py`, which copies the project and
injects prohibited imports to prove nonzero exits. No SDK installation or live
service is needed. This fixture demonstrates enforcement, not a comprehensive
Python import analyzer; real projects choose tooling that covers their import
syntax and dependency graph.
