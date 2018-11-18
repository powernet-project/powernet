CREATE TABLE input_sources (id integer primary key autoincrement, type TEXT, name TEXT, api_id TEXT);
CREATE TABLE input_sources_state (id integer primary key, state TEXT, currentdate text, currenttime text, source_id integer not null, foreign key (source_id) references input_sources(id));
CREATE TABLE measurements (id integer primary key, rms integer, currentdate text, currenttime text, source_id integer not null, foreign key (source_id) references input_sources(id));
