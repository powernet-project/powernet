CREATE TABLE input_sources (id integer primary key autoincrement, type TEXT, name TEXT);
CREATE TABLE input_sources_state (id integer primary key, state TEXT, currentdate text, currenttime text, source_id integer not null, foreign key (source_id) references input_sources(id));
CREATE TABLE measurements (id integer primary key, rms integer, currentdate text, currenttime text, source_id integer not null, foreign key (source_id) references input_sources(id));

INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch0");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch1");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch2");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch3");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch4");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch5");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch6");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "ch7");