"""从旧系统数据库导入种子数据到 V2。

用法：
    cd v2/backend
    source .venv/bin/activate
    PYTHONPATH=. python scripts/seed_from_legacy.py --project-id 2 --limit 50
"""
import argparse
from datetime import datetime

from sqlalchemy import create_engine, text

from app.db.session import SessionLocal
from app.models.content import Comment, Content
from app.models.creator import Creator
from app.models.project import Project

LEGACY_DB_URL = "postgresql://root@localhost:5432/xiaolongxia_analytics"


def _map_platform(platform: str) -> str:
    return "douyin" if platform == "dy" else platform


def import_data(project_id: int, limit: int = 50) -> None:
    legacy_engine = create_engine(LEGACY_DB_URL)
    db = SessionLocal()

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    with legacy_engine.connect() as legacy_conn:
        # 导入创作者
        creator_rows = legacy_conn.execute(
            text(
                """
                SELECT id, platform, platform_creator_id, nickname, avatar_url,
                       follower_count, following_count, liked_count
                FROM creators
                WHERE platform IN ('dy', 'xhs')
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()

        creator_id_map: dict[int, int] = {}
        for row in creator_rows:
            existing = (
                db.query(Creator)
                .filter(
                    Creator.project_id == project_id,
                    Creator.platform == _map_platform(row["platform"]),
                    Creator.platform_creator_id == str(row["platform_creator_id"] or ""),
                )
                .first()
            )
            if existing:
                creator_id_map[row["id"]] = existing.id
                continue
            creator = Creator(
                project_id=project_id,
                platform=_map_platform(row["platform"]),
                platform_creator_id=str(row["platform_creator_id"] or ""),
                nickname=row["nickname"],
                avatar_url=row["avatar_url"],
                follower_count=row["follower_count"],
                following_count=row["following_count"],
                total_likes=row["liked_count"],
            )
            db.add(creator)
            db.commit()
            db.refresh(creator)
            creator_id_map[row["id"]] = creator.id

        print(f"Imported {len(creator_id_map)} creators")

        # 导入内容
        content_rows = legacy_conn.execute(
            text(
                """
                SELECT id, platform, platform_content_id, creator_id, source_url, title,
                       body_text, content_type, like_count, comment_count, share_count,
                       play_count, collect_count, cover_url, video_download_url,
                       published_at, created_at
                FROM contents
                WHERE platform IN ('dy', 'xhs')
                ORDER BY published_at DESC NULLS LAST
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()

        content_id_map: dict[int, int] = {}
        for row in content_rows:
            existing = (
                db.query(Content)
                .filter(
                    Content.project_id == project_id,
                    Content.platform == _map_platform(row["platform"]),
                    Content.platform_content_id == str(row["platform_content_id"] or ""),
                )
                .first()
            )
            if existing:
                content_id_map[row["id"]] = existing.id
                continue

            # 关联创作者：旧系统有 creator_id 字段
            creator_id = None
            if row["creator_id"]:
                creator_id = creator_id_map.get(row["creator_id"])

            content = Content(
                project_id=project_id,
                creator_id=creator_id,
                platform=_map_platform(row["platform"]),
                platform_content_id=str(row["platform_content_id"] or ""),
                url=row["source_url"],
                title=row["title"],
                description=row["body_text"],
                content_type=row["content_type"],
                likes=row["like_count"],
                comments=row["comment_count"],
                shares=row["share_count"],
                views=row["play_count"],
                collections=row["collect_count"],
                cover_url=row["cover_url"],
                video_url=row["video_download_url"],
                published_at=row["published_at"],
                crawled_at=row["created_at"] or datetime.utcnow(),

            )
            db.add(content)
            db.commit()
            db.refresh(content)
            content_id_map[row["id"]] = content.id

        print(f"Imported {len(content_id_map)} contents")

        # 导入评论
        if content_id_map:
            comment_rows = legacy_conn.execute(
                text(
                    """
                    SELECT id, content_id, platform_comment_id, platform_user_id,
                           nickname, content, like_count, reply_count, commented_at
                    FROM comments
                    WHERE content_id IN :content_ids
                    LIMIT :limit
                    """
                ),
                {"content_ids": tuple(content_id_map.keys()), "limit": limit * 20},
            ).mappings().all()

            count = 0
            for row in comment_rows:
                new_content_id = content_id_map.get(row["content_id"])
                if not new_content_id:
                    continue
                comment = Comment(
                    content_id=new_content_id,
                    platform_comment_id=str(row["platform_comment_id"] or ""),
                    platform_user_id=str(row["platform_user_id"] or ""),
                    nickname=row["nickname"],
                    text=row["content"],
                    likes=row["like_count"],
                    replies=row["reply_count"],
                    replied_at=row["commented_at"],
                )
                db.add(comment)
                count += 1
                if count % 100 == 0:
                    db.commit()
            db.commit()

            print(f"Imported {count} comments")

    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", type=int, required=True)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    import_data(args.project_id, args.limit)
