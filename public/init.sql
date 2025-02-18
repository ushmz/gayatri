DROP TABLE IF EXISTS behavior_log;
CREATE TABLE behavior_log(
    id INTEGER AUTO_INCREMENT,
    uid VARCHAR(36),
    task_name VARCHAR(36),
    time_on_page INTEGER,
    current_page INTEGER,
    position_on_page INTEGER,
    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS click_log_doc;
CREATE TABLE click_log_doc(
    id INTEGER AUTO_INCREMENT,
    uid VARCHAR(36),
    task_name VARCHAR(36),
    time_on_page INTEGER,
    page_url VARCHAR(4096),
    linked_page_num INTEGER,
    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS click_log_history;
CREATE TABLE click_log_history(
    id INTEGER AUTO_INCREMENT,
    uid VARCHAR(36),
    task_name VARCHAR(36),
    time_on_page INTEGER,
    linked_doc_url VARCHAR(4096),
    linked_page_num INTEGER,
    collapse BOOLEAN,
    PRIMARY KEY(id)
);
