import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Exercise the tools from a calling project, keeping dependency caches out of skills.
const project = mkdtempSync(join(tmpdir(), "pstack-tools-test-"));
let exitCode = 1;
try {
  const result = Bun.spawnSync([
    process.execPath,
    "test",
    ...["orch", "watch-pr", "check-plan.test.ts"].map((path) => join(import.meta.dir, path)),
  ], { cwd: project, stdout: "inherit", stderr: "inherit" });
  exitCode = result.exitCode;
} finally {
  rmSync(project, { recursive: true, force: true });
}
process.exit(exitCode);
