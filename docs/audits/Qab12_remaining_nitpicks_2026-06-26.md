Historical Qab12 nitpicks, 26 June 2026

These comments were written against the previous version of `Qab12.tex` and
the then-current auxiliary files.  The live items were addressed in the
subsequent revision that promoted `Qab12_revised.tex` to the current
manuscript source, now named `Qab.tex`.

Remaining non-blocking cleanup issues

These do not appear to undermine the proof, but I would fix them before treating the archive as final.

1. The paper still references a few stale paths

The then-current manuscript still referred to paths that were not present at
the root of the current bundle:

code/certify_constants.py
code/certify_thresholds.sage
code/lower/endpoint_state.schema.json

The first two appear to refer to archived upper-range material now located under:

archive/Qab9_upper_bundle/code/

The third schema file does not appear to be present. Since the current lower computation is represented by code/qab12 CSV generators/verifiers instead, I would either remove this sentence or replace it with references to the current Qab12 artifacts.

This is documentation-level, not a mathematical gap.

2. QAB12_SUMMARY.json has a stale manifest hash

The file

data/qab12/QAB12_SUMMARY.json

contains:

"manifest_sha256": "0a462f9173364836cd245e39db485a6b207da5028edf4fc7b7a535df901c581d"

for the one-nonunit-all manifest, but the actual current hash is:

1c3cb7a53691e6ff8829d16dbfd0ef28ba4d17944148b09eb162d518620216b4

The more important QAB12_BRANCH_MANIFEST.json has the correct hash, and the manifest verifier passes, so this is not a proof issue. Still, it is worth fixing.

3. SHA256SUMS does not literally hash every file except itself

The README says SHA256SUMS hashes every file in the bundle excluding itself. In fact, it omits at least:

ARTIFACT_MANIFEST.json
archive/Qab9_upper_bundle/SHA256SUMS

ARTIFACT_MANIFEST.json does hash those files, so the archive is still checkable, but the README wording should be adjusted or SHA256SUMS should be regenerated.

4. Some stored logs are stale relative to the current Makefile

For example:

logs/qab12_verify_light_final.txt
logs/qab12_verify_light_rerun.txt

still show the old flags:

-std=c++20 -Wpedantic

and do not include the newly added residual and all-manifest verification steps from the current q12-verify-light target.

The active Makefile and verifiers are correct; the logs just need regeneration or relabeling as historical.

5. The bundled audit reports now contain obsolete negative statements

The package includes older audit files such as:

docs/audits/Qab12_audit_report.md
docs/audits/Qab13_audit.md

These contain now-obsolete statements about the residual branch remaining or manifests being stale. That is fine as audit history, but the README currently calls them “current-stage external audit reports,” which could confuse a referee. I would relabel them as historical audits, or add a short note saying their issues have been addressed in the current archive.
