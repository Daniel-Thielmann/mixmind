import { createClient } from "@libsql/client";
import { drizzle } from "drizzle-orm/libsql";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import * as schema from "@/db/schema";

const dataDirectory = join(process.cwd(), "data");
mkdirSync(dataDirectory, { recursive: true });

const client = createClient({
  url: `file:${join(dataDirectory, "mixmind.db")}`,
});

export const db = drizzle(client, { schema });
export type DbClient = typeof db;
