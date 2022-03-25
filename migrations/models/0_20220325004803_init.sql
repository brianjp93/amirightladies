-- upgrade --
CREATE TABLE IF NOT EXISTS "guild" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "exid" INT NOT NULL
);
CREATE TABLE IF NOT EXISTS "member" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "exid" INT NOT NULL,
    "name" VARCHAR(128) NOT NULL,
    "nick" VARCHAR(64),
    "discriminator" VARCHAR(64) NOT NULL,
    "bot" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "song" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "stream_id" VARCHAR(512) NOT NULL UNIQUE,
    "title" VARCHAR(512) NOT NULL,
    "url" VARCHAR(512) NOT NULL,
    "file" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "defersong" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "query" VARCHAR(128) NOT NULL  DEFAULT '',
    "sort_int" INT NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "guild_id" INT REFERENCES "guild" ("id") ON DELETE CASCADE,
    "song_id" INT REFERENCES "song" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_defersong_guild_i_f81b37" UNIQUE ("guild_id", "sort_int")
);
CREATE INDEX IF NOT EXISTS "idx_defersong_sort_in_6e5611" ON "defersong" ("sort_int");
CREATE TABLE IF NOT EXISTS "historysong" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "guild_id" INT NOT NULL REFERENCES "guild" ("id") ON DELETE CASCADE,
    "song_id" INT NOT NULL REFERENCES "song" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "member_guild" (
    "member_id" INT NOT NULL REFERENCES "member" ("id") ON DELETE CASCADE,
    "guild_id" INT NOT NULL REFERENCES "guild" ("id") ON DELETE CASCADE
);
