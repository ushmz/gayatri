BEHAVIOR_LOG_QUERT = (
    "INSERT INTO behavior_log(uid, task_name, time_on_page, current_page, position_on_page)"
    "VALUES(%s, %s, %s, %s, %s)"
)


CLICK_DOC_LOG_QUERY = (
    "INSERT INTO click_log_doc(uid, task_name, time_on_page, page_url, linked_page_num)"
    "VALUES(%s, %s, %s, %s, %s)"
)


CLICK_HISTORY_LOG_QUERY = (
    "INSERT INTO click_log_history(uid, task_name, time_on_page, linked_doc_url, linked_page_num, collapse)"
    "VALUES(%s, %s, %s, %s, %s, %s)"
)
