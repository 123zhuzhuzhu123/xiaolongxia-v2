"""采集任务同步执行：调用 Downloader，解析并入库。"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.content import Comment, Content
from app.models.creator import Creator
from app.models.crawl_job import CrawlJob
from app.services import content as content_service
from app.services import creator as creator_service
from app.services.ingestion.crawl_job import update_job_status
from app.services.ingestion.downloader import fetch_content_detail


def _parse_platform_id(platform: str, raw: dict) -> str:
    if platform == "douyin":
        return str(raw.get("aweme_id") or raw.get("id") or "")
    if platform == "xhs":
        return str(raw.get("note_id") or raw.get("id") or "")
    return str(raw.get("id") or "")


def _find_or_create_creator(
    db: Session, project_id: int, platform: str, raw_creator: dict
) -> Creator:
    platform_creator_id = str(
        raw_creator.get("uid") or raw_creator.get("user_id") or ""
    )
    creator = creator_service.get_creator_by_platform_id(
        db, project_id, platform, platform_creator_id
    )
    if creator:
        return creator
    return Creator(
        project_id=project_id,
        platform=platform,
        platform_creator_id=platform_creator_id,
        nickname=raw_creator.get("nickname") or raw_creator.get("nick_name"),
        avatar_url=raw_creator.get("avatar"),
        follower_count=raw_creator.get("follower_count"),
        total_likes=raw_creator.get("total_favorited"),
    )


def run_crawl_job(db: Session, job: CrawlJob) -> CrawlJob:
    """同步执行采集任务并入库。"""
    job.started_at = datetime.utcnow()
    update_job_status(db, job, "running")

    try:
        raw = fetch_content_detail(job.platform, job.target_value)
        data = raw.get("data") or raw

        # 创作者
        raw_creator = data.get("creator") or data.get("author") or {}
        creator = _find_or_create_creator(db, job.project_id, job.platform, raw_creator)
        if creator.id is None:
            db.add(creator)
            db.commit()
            db.refresh(creator)

        # 内容
        platform_content_id = _parse_platform_id(job.platform, data)
        content = content_service.get_content_by_platform_id(
            db, job.project_id, job.platform, platform_content_id
        )
        if not content:
            published_at = None
            create_time = data.get("create_time")
            if create_time:
                try:
                    published_at = datetime.fromtimestamp(int(create_time))
                except (ValueError, TypeError):
                    pass

            content = Content(
                project_id=job.project_id,
                creator_id=creator.id,
                platform=job.platform,
                platform_content_id=platform_content_id,
                url=job.target_value,
                title=data.get("title") or data.get("desc"),
                description=data.get("desc"),
                content_type="video" if job.platform == "douyin" else "image_text",
                likes=data.get("digg_count") or data.get("liked_count"),
                comments=data.get("comment_count"),
                shares=data.get("share_count"),
                views=data.get("play_count") or data.get("view_count"),
                collections=data.get("collect_count"),
                cover_url=data.get("cover"),
                video_url=data.get("video_url") or data.get("video_play_url"),
                published_at=published_at,
            )
            db.add(content)
            db.commit()
            db.refresh(content)

        # 评论
        raw_comments = data.get("comments") or []
        for rc in raw_comments:
            comment = Comment(
                content_id=content.id,
                platform_comment_id=str(
                    rc.get("comment_id") or rc.get("cid") or ""
                ),
                platform_user_id=str(rc.get("user_id") or rc.get("uid") or ""),
                nickname=rc.get("nickname"),
                text=rc.get("text") or rc.get("content") or "",
                likes=rc.get("digg_count") or rc.get("like_count"),
                replies=rc.get("reply_comment_total"),
            )
            db.add(comment)
        db.commit()

        return update_job_status(
            db,
            job,
            "completed",
            items_crawled=len(raw_comments),
            result_summary={"content_id": content.id, "creator_id": creator.id},
            finished_at=datetime.utcnow(),
        )
    except Exception as e:
        db.rollback()
        return update_job_status(
            db, job, "failed", error_message=str(e), finished_at=datetime.utcnow()
        )
