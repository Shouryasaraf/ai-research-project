# Experiment Result Schema

`experiment_records.py` writes one exclusive-create JSON file per run. Existing records cannot be silently overwritten.

Required identity and provenance fields:

- run, scenario, and policy identifiers;
- non-negative random seed;
- explicit synthetic-input flag;
- completed, failed, or interrupted status;
- start and finish timestamps;
- canonical configuration SHA-256;
- environment metadata;
- notes and limitations.

Metrics are divided into separate `measured_metrics` and `modeled_metrics` objects. Carbon estimates, risk exposure, utility scores, and other calculated quantities must not be placed in the measured group unless directly measured by a declared instrument or observation procedure.

Failed and interrupted runs remain records and must not be silently dropped from the experiment inventory.

