import fs from 'fs';
import path from 'path';
import url from 'url';
import { pool, query } from './db.js';

async function ensureMigrationsTable() {
  await query(
    `CREATE TABLE IF NOT EXISTS schema_migrations (
      version TEXT PRIMARY KEY,
      applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )`
  );
}

async function appliedVersions(): Promise<Set<string>> {
  const { rows } = await query<{ version: string }>('SELECT version FROM schema_migrations');
  return new Set(rows.map((r: { version: string }) => r.version));
}

async function applyMigration(filePath: string, version: string) {
  const sql = fs.readFileSync(filePath, 'utf8');
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query(sql);
    await client.query('INSERT INTO schema_migrations(version) VALUES($1)', [version]);
    await client.query('COMMIT');
    console.log(`Applied migration ${version}`);
  } catch (err) {
    await client.query('ROLLBACK');
    console.error(`Failed migration ${version}`, err);
    throw err;
  } finally {
    client.release();
  }
}

async function main() {
  const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
  const migrationsDir = path.resolve(__dirname, '../migrations');
  await ensureMigrationsTable();
  const applied = await appliedVersions();
  const files = fs
    .readdirSync(migrationsDir)
    .filter((f: string) => f.endsWith('.sql'))
    .sort();

  for (const file of files) {
    const version = path.basename(file, '.sql');
    if (applied.has(version)) continue;
    await applyMigration(path.join(migrationsDir, file), version);
  }
  console.log('Migrations complete');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
