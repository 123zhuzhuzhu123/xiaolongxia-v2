"""导入所有模型以注册到 Base.metadata。"""
from app.models.content import Comment, Content
from app.models.copy import CopyDraft, CopyVersion
from app.models.crawl_job import CrawlJob
from app.models.creator import Creator
from app.models.formula import Formula
from app.models.hook import Hook
from app.models.project import Project, User
from app.models.sku import Sku
