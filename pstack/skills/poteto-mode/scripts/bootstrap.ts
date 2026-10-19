import { createHash } from "node:crypto";
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { isAbsolute, join, relative, sep } from "node:path";
import { pathToFileURL } from "node:url";

const scriptsDirectory = realpathSync(import.meta.dir);

function within(parent: string, child: string): boolean {
  const path = relative(parent, child);
  return path === "" || (path !== ".." && !path.startsWith(`..${sep}`) && !isAbsolute(path));
}

export function ensureDependenciesInstalled(): string {
  const project = realpathSync(process.cwd());
  const skillDirectory = realpathSync(join(scriptsDirectory, ".."));
  if (within(skillDirectory, project)) {
    throw new Error("Run poteto tools from the calling project, not the installed skill directory");
  }
  const packageBytes = readFileSync(join(scriptsDirectory, "package.json"));
  const lockBytes = readFileSync(join(scriptsDirectory, "bun.lock"));
  const key = createHash("sha256").update(packageBytes).update("\0").update(lockBytes).digest("hex");
  let runtimeRoot = project;
  for (const component of [".pstack", "runtime", "poteto-tools"]) {
    runtimeRoot = join(runtimeRoot, component);
    if (existsSync(runtimeRoot) && lstatSync(runtimeRoot).isSymbolicLink()) {
      throw new Error(`Refusing linked runtime path: ${runtimeRoot}`);
    }
  }
  const directory = join(runtimeRoot, key);
  if (existsSync(directory) && lstatSync(directory).isSymbolicLink()) throw new Error("Refusing linked dependency cache");
  const commander = join(directory, "node_modules", "commander", "index.js");
  const marker = join(directory, ".install-key");
  if (existsSync(commander) && existsSync(marker) && readFileSync(marker, "utf8").trim() === key) return directory;
  if (existsSync(directory)) throw new Error(`Incomplete dependency cache; remove this calling-project cache and retry: ${directory}`);
  mkdirSync(runtimeRoot, { recursive: true, mode: 0o700 });
  if (!within(project, realpathSync(runtimeRoot)) || within(skillDirectory, realpathSync(runtimeRoot))) {
    throw new Error("Dependency cache must remain in the calling project");
  }
  const temporary = mkdtempSync(join(runtimeRoot, ".install-"));
  try {
    writeFileSync(join(temporary, "package.json"), packageBytes);
    writeFileSync(join(temporary, "bun.lock"), lockBytes);
    const result = Bun.spawnSync([process.execPath, "install", "--frozen-lockfile"], {
      cwd: temporary,
      env: { ...process.env, BUN_INSTALL_CACHE_DIR: join(runtimeRoot, ".bun-cache") },
    });
    if (result.exitCode !== 0) {
      process.stdout.write(result.stdout);
      process.stderr.write(result.stderr);
      throw new Error(`bun install --frozen-lockfile exited with status ${result.exitCode}`);
    }
    if (!existsSync(join(temporary, "node_modules", "commander", "index.js"))) throw new Error("Dependency install completed without commander");
    writeFileSync(join(temporary, ".install-key"), `${key}\n`);
    try {
      renameSync(temporary, directory);
    } catch (error) {
      if (!existsSync(commander) || !existsSync(marker) || readFileSync(marker, "utf8").trim() !== key) throw error;
    }
    return directory;
  } finally {
    rmSync(temporary, { recursive: true, force: true });
  }
}

export function commanderModuleURL(): string {
  return pathToFileURL(join(ensureDependenciesInstalled(), "node_modules", "commander", "index.js")).href;
}

export async function loadCommander(): Promise<typeof import("commander")> {
  return import(commanderModuleURL());
}
