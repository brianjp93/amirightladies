-- upgrade --
ALTER TABLE "guild" ALTER COLUMN "exid" TYPE BIGINT USING "exid"::BIGINT;
ALTER TABLE "member" ALTER COLUMN "exid" TYPE BIGINT USING "exid"::BIGINT;
-- downgrade --
ALTER TABLE "guild" ALTER COLUMN "exid" TYPE INT USING "exid"::INT;
ALTER TABLE "member" ALTER COLUMN "exid" TYPE INT USING "exid"::INT;
