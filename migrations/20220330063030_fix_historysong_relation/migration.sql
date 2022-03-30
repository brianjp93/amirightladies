/*
  Warnings:

  - A unique constraint covering the columns `[song_id]` on the table `DeferSong` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[guild_id,sort_int]` on the table `DeferSong` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[exid]` on the table `Guild` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[exid]` on the table `Member` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[A,B]` on the table `_GuildToMember` will be added. If there are existing duplicate values, this will fail.

*/
-- DropIndex
DROP INDEX "DeferSong_guild_id_sort_int_key";

-- DropIndex
DROP INDEX "DeferSong_song_id_key";

-- DropIndex
DROP INDEX "DeferSong_sort_int_idx";

-- DropIndex
DROP INDEX "Guild_exid_key";

-- DropIndex
DROP INDEX "HistorySong_created_at_idx";

-- DropIndex
DROP INDEX "HistorySong_song_id_key";

-- DropIndex
DROP INDEX "Member_exid_key";

-- DropIndex
DROP INDEX "_GuildToMember_AB_unique";

-- DropIndex
DROP INDEX "_GuildToMember_B_index";

-- CreateIndex
CREATE UNIQUE INDEX "DeferSong_song_id_key" ON "DeferSong"("song_id");

-- CreateIndex
CREATE INDEX "DeferSong_sort_int_idx" ON "DeferSong"("sort_int");

-- CreateIndex
CREATE UNIQUE INDEX "DeferSong_guild_id_sort_int_key" ON "DeferSong"("guild_id", "sort_int");

-- CreateIndex
CREATE UNIQUE INDEX "Guild_exid_key" ON "Guild"("exid");

-- CreateIndex
CREATE INDEX "HistorySong_created_at_idx" ON "HistorySong"("created_at");

-- CreateIndex
CREATE UNIQUE INDEX "Member_exid_key" ON "Member"("exid");

-- CreateIndex
CREATE UNIQUE INDEX "_GuildToMember_AB_unique" ON "_GuildToMember"("A", "B");

-- CreateIndex
CREATE INDEX "_GuildToMember_B_index" ON "_GuildToMember"("B");
