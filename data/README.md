# Empty on purpose

No message may be collected until the protocol is approved and the consent form is filled.
`scripts/sms_collect.py --check` says what is still missing. If this directory ever holds data while that
command still reports `ready_to_collect: false`, something was collected that should not have
been, and it cannot be fixed afterwards — consent is not obtainable retroactively.
