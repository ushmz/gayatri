from pydantic import BaseModel

from consts import BEHAVIOR_LOG_QUERT, CLICK_DOC_LOG_QUERY, CLICK_HISTORY_LOG_QUERY


class BehaviorLoggingRequest(BaseModel):
    uid: str
    timeOnPage: int
    currentPage: int
    positionOnPage: int

    def queryalize(self) -> str:
        return BEHAVIOR_LOG_QUERT.format(
            self.uid, self.timeOnPage, self.currentPage, self.positionOnPage
        )


class DocumentLoggingRequest(BaseModel):
    uid: str
    timeOnPage: int
    pageUrl: str
    linkedPageNum: int

    def queryalize(self) -> str:
        return CLICK_DOC_LOG_QUERY.format(
            self.uid, self.timeOnPage, self.pageUrl, self.linkedPageNum
        )


class HistoryLoggingRequest(BaseModel):
    uid: str
    timeOnPage: int
    linkedDocumentUrl: str
    linkedPageNum: int
    collapse: bool

    def queryalize(self) -> str:
        return CLICK_HISTORY_LOG_QUERY.format(
            self.uid,
            self.timeOnPage,
            self.linkedDocumentUrl,
            self.linkedPageNum,
            self.collapse,
        )


class XrayAnalyseRequest(BaseModel):
    uid: str
    url: str


class CipherTestRequest(BaseModel):
    text: str
