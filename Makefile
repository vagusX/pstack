# Tests for the source-based host adaptation. No legacy portable build is imported.
.PHONY: test-upstream test-upstream-install
test-upstream:
	node --test skills/pstack-host/setup/setup.test.mjs skills/pstack-host/benny-tools/test-benny.mjs
	bun test --timeout 120000 skills/poteto-mode/scripts/orch skills/poteto-mode/scripts/watch-pr skills/poteto-mode/scripts/check-plan.test.ts skills/poteto-mode/scripts/bootstrap.test.ts

test-upstream-install:
	node tests/upstream-install.mjs
