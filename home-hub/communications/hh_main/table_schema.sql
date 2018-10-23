CREATE TABLE input_sources (id integer primary key autoincrement, type TEXT, name TEXT);
CREATE TABLE input_sources_state (id integer primary key, state TEXT, currentdate text, currenttime text, source_id integer not null, foreign key (source_id) references input_sources(id));
CREATE TABLE measurements (id integer primary key, rms integer, currentdate text, currenttime text, source_id integer not null, foreign key (source_id) references input_sources(id));

INSERT INTO input_sources (type, name) VALUES ("subcircuit", "mains1");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "mains2");
INSERT INTO input_sources (type, name) VALUES ("appliance", "DW");
INSERT INTO input_sources (type, name) VALUES ("appliance", "RF");
INSERT INTO input_sources (type, name) VALUES ("subcircuit", "LT");
INSERT INTO input_sources (type, name) VALUES ("appliance", "MW");
INSERT INTO input_sources (type, name) VALUES ("appliance", "WD1");
INSERT INTO input_sources (type, name) VALUES ("appliance", "WD2");
INSERT INTO input_sources (type, name) VALUES ("appliance", "Range1");
INSERT INTO input_sources (type, name) VALUES ("appliance", "Range2");
