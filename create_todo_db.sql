BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Todo" (
	"id"	INTEGER NOT NULL UNIQUE,
	"title"	TEXT NOT NULL,
	"completed"	INTEGER DEFAULT 0,
	"url"	TEXT,
	"order"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Tag" (
	"id"	INTEGER NOT NULL UNIQUE,
	"title"	TEXT NOT NULL,
	"url"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Todo_Tag" (
	"id"	INTEGER NOT NULL UNIQUE,
	"todo_id"	INTEGER,
	"tag_id"	INTEGER,
	FOREIGN KEY("todo_id") REFERENCES "Todo"("id"),
	FOREIGN KEY("tag_id") REFERENCES "Tag"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "Todo" VALUES (1,'Finish mini project',0,'',1);
INSERT INTO "Todo" VALUES (2,'Pass gonogo',0,'',2);
INSERT INTO "Tag" VALUES (1,'Fun',NULL);
INSERT INTO "Tag" VALUES (2,'Work',NULL);
INSERT INTO "Todo_Tag" VALUES (1,1,2);
COMMIT;
