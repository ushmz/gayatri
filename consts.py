BEHAVIOR_LOG_QUERT = (
    "INSERT INTO behavior_log(ext_id, time_on_page, current_page, position_on_page)"
    "VALUES(%s, %s, %s, %s)"
)


CLICK_DOC_LOG_QUERY = (
    "INSERT INTO click_log_doc(ext_id, page_url, linked_page_num)" "VALUES(%s, %s, %s)"
)


CLICK_HISTORY_LOG_QUERY = (
    "INSERT INTO click_log_history(ext_id, linked_doc_url, linked_page_num)"
    "VALUES(%s, %s, %s)"
)
