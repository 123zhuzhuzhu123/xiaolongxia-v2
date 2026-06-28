"""导入默认文案生产资产。"""
import argparse

from app.db.session import SessionLocal
from app.schemas.copywriter import FormulaCreate, HookCreate, SkuCreate
from app.services.copywriter import assets

DEFAULT_FORMULAS = [
    {
        "formula_key": "pain_conflict",
        "name": "痛点冲突",
        "goal": "conversion",
        "template": "你有没有遇到过【痛点】？\n我之前也是，【共鸣经历】。\n后来试了【产品】，【改变点】。\n现在【美好结果】。\n如果你也【人群标签】，真的可以试试。",
        "description": "先戳痛点，再给解决方案，适合转化",
        "tags": ["痛点", "转化"],
    },
    {
        "formula_key": "result_first",
        "name": "结果先行",
        "goal": "conversion",
        "template": "【惊艳结果】！\n很多人问我怎么做到的。\n其实就用了【产品】，【核心卖点】。\n【使用场景/细节】。\n想要【结果】的姐妹，别错过。",
        "description": "开头直接展示结果，吸引眼球",
        "tags": ["结果", "吸睛"],
    },
    {
        "formula_key": "trust_proof",
        "name": "信任背书",
        "goal": "conversion",
        "template": "【销量/口碑数据】的【产品】，到底凭什么？\n我扒了一下，发现【成分/技术/卖点】。\n【用户真实反馈】。\n【适用人群】可以闭眼入。",
        "description": "用数据和口碑建立信任",
        "tags": ["信任", "数据"],
    },
    {
        "formula_key": "identity_resonance",
        "name": "身份共鸣",
        "goal": "engagement",
        "template": "【身份标签】才懂的事。\n【具体场景】。\n是不是你也在找【解决方案】？\n评论区聊聊。",
        "description": "用身份标签引发共鸣和互动",
        "tags": ["共鸣", "互动"],
    },
    {
        "formula_key": "scarcity_hook",
        "name": "稀缺紧迫感",
        "goal": "conversion",
        "template": "【产品】终于【活动/补货】了！\n上次没抢到的姐妹这次抓紧。\n【核心卖点】。\n【限时/限量信息】。\n链接在【位置】。",
        "description": "营造稀缺感促转化",
        "tags": ["稀缺", "促销"],
    },
]

DEFAULT_HOOKS = [
    {"hook_type": "pain", "text": "你是不是也总为【问题】发愁？"},
    {"hook_type": "result", "text": "【结果】我真的做到了！"},
    {"hook_type": "question", "text": "【产品】到底值不值得买？"},
    {"hook_type": "story", "text": "讲一个我踩过的坑。"},
    {"hook_type": "scarcity", "text": "这个价真的快没有了。"},
]

DEFAULT_SKUS = [
    {
        "sku_name": "紫盖湿巾 80抽*6包",
        "brand_name": "Babycare",
        "category": "母婴湿巾",
        "selling_points": ["加厚锁湿", "不掉絮", "海绵宝宝联名"],
        "marketing_brief": "主打带娃清洁自由，强调锁湿不掉絮和联名款颜值",
        "price_range": "50-80",
        "target_users": ["0-3岁宝妈", "注重颜值的妈妈"],
    },
    {
        "sku_name": "婴儿纸尿裤 NB码",
        "brand_name": "示例品牌",
        "category": "纸尿裤",
        "selling_points": ["超薄透气", "弱酸表层", " overnight 不漏"],
        "marketing_brief": "针对新生儿敏感肌，强调透气和防漏",
        "price_range": "80-120",
        "target_users": ["新生儿妈妈", "敏感肌宝宝家长"],
    },
]


def seed(project_id: int) -> None:
    db = SessionLocal()

    for f in DEFAULT_FORMULAS:
        existing = (
            db.query(assets.Formula)
            .filter(
                assets.Formula.project_id == project_id,
                assets.Formula.formula_key == f["formula_key"],
            )
            .first()
        )
        if not existing:
            assets.create_formula(
                db,
                FormulaCreate(project_id=project_id, **f),
            )

    for h in DEFAULT_HOOKS:
        existing = (
            db.query(assets.Hook)
            .filter(
                assets.Hook.project_id == project_id,
                assets.Hook.text == h["text"],
            )
            .first()
        )
        if not existing:
            assets.create_hook(
                db,
                HookCreate(project_id=project_id, **h),
            )

    for s in DEFAULT_SKUS:
        existing = (
            db.query(assets.Sku)
            .filter(
                assets.Sku.project_id == project_id,
                assets.Sku.sku_name == s["sku_name"],
            )
            .first()
        )
        if not existing:
            assets.create_sku(
                db,
                SkuCreate(project_id=project_id, **s),
            )

    db.close()
    print(f"Seeded copywriter assets for project {project_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", type=int, required=True)
    args = parser.parse_args()
    seed(args.project_id)
