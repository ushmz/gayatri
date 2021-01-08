DROP TABLE IF EXISTS behavior_log;
CREATE TABLE behavior_log(
    id INTEGER AUTO_INCREMENT,
    ext_id VARCHAR(32),
    time_on_page INTEGER,
    current_page INTEGER,
    position_on_page INTEGER,
    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS click_log_doc;
CREATE TABLE click_log_doc(
    id INTEGER AUTO_INCREMENT,
    ext_id VARCHAR(32),
    page_url VARCHAR(4096),
    linked_page_num INTEGER,
    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS click_log_history;
CREATE TABLE click_log_history(
    id INTEGER AUTO_INCREMENT,
    ext_id VARCHAR(32),
    linked_doc_url VARCHAR(4096),
    linked_page_num INTEGER,
    PRIMARY KEY(id)
);
