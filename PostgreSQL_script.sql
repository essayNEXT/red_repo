CREATE TABLE "users" (
  "id" int PRIMARY KEY,
  "first_name" varchar,
  "last_name" varchar,
  "telegram_id" varchar,
  "language_id" int
);

CREATE TABLE "dictionaries" (
  "id" int PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "dictionaries_langueges" (
  "dictionary_id" int,
  "name" varchar,
  "language_from_id" int,
  "language_to_id" int
);

CREATE TABLE "languages" (
  "id" int PRIMARY KEY,
  "name" varchar NOT NULL,
  "identifier" varchar NOT NULL
);

CREATE TABLE "entities" (
  "id" int,
  "value" varchar NOT NULL,
  "language_id" int
);

CREATE TABLE "entities_translations" (
  "id" int,
  "essence_id" int,
  "essence_interpretation_id" int,
  "language_id" int,
  "dictionary_id" int
);

CREATE TABLE "essences_interpretation" (
  "id" int,
  "essence_id" int,
  "value" varchar
);

ALTER TABLE "users" ADD FOREIGN KEY ("language_id") REFERENCES "languages" ("id");

ALTER TABLE "dictionaries_langueges" ADD FOREIGN KEY ("dictionary_id") REFERENCES "dictionaries" ("id");

ALTER TABLE "dictionaries_langueges" ADD FOREIGN KEY ("language_from_id") REFERENCES "languages" ("id");

ALTER TABLE "dictionaries_langueges" ADD FOREIGN KEY ("language_to_id") REFERENCES "languages" ("id");

ALTER TABLE "entities" ADD FOREIGN KEY ("language_id") REFERENCES "languages" ("id");

ALTER TABLE "entities_translations" ADD FOREIGN KEY ("essence_id") REFERENCES "entities" ("id");

ALTER TABLE "entities_translations" ADD FOREIGN KEY ("essence_interpretation_id") REFERENCES "essences_interpretation" ("id");

ALTER TABLE "entities_translations" ADD FOREIGN KEY ("language_id") REFERENCES "languages" ("id");

ALTER TABLE "entities_translations" ADD FOREIGN KEY ("dictionary_id") REFERENCES "dictionaries" ("id");

ALTER TABLE "essences_interpretation" ADD FOREIGN KEY ("essence_id") REFERENCES "entities" ("id");
