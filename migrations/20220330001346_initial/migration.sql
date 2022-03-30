-- CreateTable
CREATE TABLE "HistorySong" (
    "id" SERIAL NOT NULL,
    "song_id" INTEGER NOT NULL,
    "guild_id" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "HistorySong_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Song" (
    "id" SERIAL NOT NULL,
    "stream_id" VARCHAR(512) NOT NULL,
    "title" VARCHAR(512) NOT NULL,
    "url" VARCHAR(512) NOT NULL,
    "file" VARCHAR(512) NOT NULL,

    CONSTRAINT "Song_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DeferSong" (
    "id" SERIAL NOT NULL,
    "query" VARCHAR(128) NOT NULL DEFAULT E'',
    "song_id" INTEGER,
    "sort_int" SERIAL NOT NULL,
    "guild_id" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "DeferSong_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Member" (
    "id" SERIAL NOT NULL,
    "exid" BIGINT NOT NULL,
    "name" VARCHAR(128) NOT NULL,
    "nick" VARCHAR(64),
    "discriminator" VARCHAR(64) NOT NULL,
    "bot" BOOLEAN NOT NULL DEFAULT false,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Member_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Guild" (
    "id" SERIAL NOT NULL,
    "exid" BIGINT NOT NULL,

    CONSTRAINT "Guild_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_GuildToMember" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "HistorySong_song_id_key" ON "HistorySong"("song_id");

-- CreateIndex
CREATE INDEX "HistorySong_created_at_idx" ON "HistorySong"("created_at");

-- CreateIndex
CREATE INDEX "DeferSong_sort_int_idx" ON "DeferSong"("sort_int");

-- CreateIndex
CREATE UNIQUE INDEX "DeferSong_guild_id_sort_int_key" ON "DeferSong"("guild_id", "sort_int");

-- CreateIndex
CREATE UNIQUE INDEX "DeferSong_song_id_key" ON "DeferSong"("song_id");

-- CreateIndex
CREATE UNIQUE INDEX "Member_exid_key" ON "Member"("exid");

-- CreateIndex
CREATE UNIQUE INDEX "Guild_exid_key" ON "Guild"("exid");

-- CreateIndex
CREATE UNIQUE INDEX "_GuildToMember_AB_unique" ON "_GuildToMember"("A", "B");

-- CreateIndex
CREATE INDEX "_GuildToMember_B_index" ON "_GuildToMember"("B");

-- AddForeignKey
ALTER TABLE "HistorySong" ADD CONSTRAINT "HistorySong_song_id_fkey" FOREIGN KEY ("song_id") REFERENCES "Song"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "HistorySong" ADD CONSTRAINT "HistorySong_guild_id_fkey" FOREIGN KEY ("guild_id") REFERENCES "Guild"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DeferSong" ADD CONSTRAINT "DeferSong_song_id_fkey" FOREIGN KEY ("song_id") REFERENCES "Song"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DeferSong" ADD CONSTRAINT "DeferSong_guild_id_fkey" FOREIGN KEY ("guild_id") REFERENCES "Guild"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_GuildToMember" ADD FOREIGN KEY ("A") REFERENCES "Guild"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_GuildToMember" ADD FOREIGN KEY ("B") REFERENCES "Member"("id") ON DELETE CASCADE ON UPDATE CASCADE;
