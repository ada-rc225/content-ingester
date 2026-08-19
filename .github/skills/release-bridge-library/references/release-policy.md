# Bridge library release policy

## Authorised transition

The gate may change only:

- library `status`: `candidate` to `released`;
- every bridge `status`: `candidate` to `released`;
- root `approval`: add the exact review identity, review hash, gate version, and
  release time.

Every other field must remain identical to the approved candidate.

## Required evidence

- Candidate validation is valid with zero errors and warnings.
- A fresh validator run against the recorded Curriculum Model and pathway/review
  pairs produces the same result except for its run timestamp.
- Review bindings match the current candidate and validation-report hashes.
- Root, overall, every bridge, and all five field decisions are approved.
- Review coverage exactly equals candidate bridge coverage and the recorded
  concept, contract, candidate, profile, RC-item, content-block, and source IDs
  match the candidate.

## Failure behaviour

Any mismatch fails the release. The gate never repairs inputs, never overwrites
an output directory, and publishes atomically so a failure leaves no partial
release.
