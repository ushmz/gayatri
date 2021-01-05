DROP TABLE IF EXISTS behavior_log;
CREATE TABLE behavior_log(
    id VARCHAR(32) PRIMARY KEY,
    time_on_page INTEGER,
    position_on_page INTEGER
);

DROP TABLE IF EXISTS click_log_doc;
CREATE TABLE click_log_doc(
    id VARCHAR(32) PRIMARY KEY,
    page_url VARCHAR(4096),
    linked_page_num INTEGER
);

DROP TABLE IF EXISTS click_log_history;
CREATE TABLE click_log_history(
    id VARCHAR(32) PRIMARY KEY,
    linked_doc_url VARCHAR(4096),
    linked_page_num INTEGER
);
