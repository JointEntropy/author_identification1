-- TABLE
CREATE TABLE "Author" (
	id BIGINT, 
	name TEXT, 
	bio TEXT, 
	img_url TEXT, 
	class_label BIGINT
);
CREATE TABLE "Composition" (
	id BIGINT, 
	title TEXT, 
	text TEXT, 
	author_id BIGINT, 
	features FLOAT
);
 
-- INDEX
CREATE INDEX "ix_Author_id" ON "Author" (id);
CREATE INDEX "ix_Composition_id" ON "Composition" (id);
 
-- TRIGGER
 
-- VIEW
 
