from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.project import Project
from app.models.rule import WarningRule
from app.models.event import WarningEvent, EVENT_STATUS_PENDING
from app.models.review import ReviewRecord
from app.services.risk_engine import risk_engine


def seed_sample_data():
    db: Session = SessionLocal()
    try:
        if db.query(Project).count() > 0:
            print("数据库已有数据，跳过初始化。")
            return

        project_a = Project(
            name="某市文旅局-舆情监测项目",
            client_name="某市文化和旅游局",
            industry="文旅政务",
            region="华东-某市",
            key_entities=["某市文旅局", "某景区", "某博物馆", "文旅局长"],
            description="监测文旅行业政策落地、景区投诉、文旅活动相关舆情",
            status="active",
        )
        project_b = Project(
            name="某银行-声誉风险监测",
            client_name="某国有银行某省分行",
            industry="金融银行",
            region="华南-某省",
            key_entities=["某银行", "某银行APP", "某银行客服", "理财经理"],
            description="监测银行服务投诉、理财产品争议、员工行为等舆情",
            status="active",
        )
        db.add_all([project_a, project_b])
        db.flush()

        rules_a = [
            WarningRule(
                project_id=project_a.id,
                name="文旅政策争议词库",
                rule_type="policy_dispute",
                keywords=["政策不合理", "文旅补贴未发放", "强制消费", "霸王条款", "暗箱操作"],
                risk_level="high",
                weight=3,
                suggested_tags=["政策争议", "文旅监管"],
                description="监测文旅相关政策执行争议类舆情",
                is_enabled=1,
            ),
            WarningRule(
                project_id=project_a.id,
                name="领导干部关联词库",
                rule_type="leader_related",
                keywords=["文旅局长", "景区主任", "文化厅", "一把手", "贪腐", "权色交易"],
                risk_level="critical",
                weight=5,
                suggested_tags=["领导干部", "廉政风险"],
                description="监测涉及文旅系统领导干部的敏感舆情",
                is_enabled=1,
            ),
            WarningRule(
                project_id=project_a.id,
                name="基层治理投诉词库",
                rule_type="governance_complaint",
                keywords=["游客投诉", "景区宰客", "强制购物", "排队太长", "退票难", "服务态度差"],
                risk_level="medium",
                weight=2,
                suggested_tags=["基层投诉", "服务质量"],
                description="监测景区和文旅服务投诉类舆情",
                is_enabled=1,
            ),
            WarningRule(
                project_id=project_a.id,
                name="突发公共事件词库",
                rule_type="public_emergency",
                keywords=["景区事故", "游客受伤", "火灾", "踩踏", "食物中毒", "疫情爆发", "山体滑坡"],
                risk_level="critical",
                weight=5,
                suggested_tags=["突发事件", "安全事故"],
                description="监测文旅场景下的突发安全类事件",
                is_enabled=1,
            ),
        ]

        rules_b = [
            WarningRule(
                project_id=project_b.id,
                name="金融政策争议词库",
                rule_type="policy_dispute",
                keywords=["降息", "降准", "房贷利率", "违规收费", "霸王条款", "阴阳合同"],
                risk_level="high",
                weight=3,
                suggested_tags=["政策争议", "金融监管"],
                description="监测金融政策和业务争议类舆情",
                is_enabled=1,
            ),
            WarningRule(
                project_id=project_b.id,
                name="银行投诉词库",
                rule_type="governance_complaint",
                keywords=["投诉银行", "APP崩了", "转账失败", "客服态度差", "乱扣费", "信用卡盗刷", "理财亏损"],
                risk_level="medium",
                weight=2,
                suggested_tags=["客户投诉", "服务问题"],
                description="监测银行服务和产品投诉",
                is_enabled=1,
            ),
            WarningRule(
                project_id=project_b.id,
                name="银行突发事件词库",
                rule_type="public_emergency",
                keywords=["银行倒闭", "挤兑", "系统瘫痪", "数据泄露", "ATM吞钱", "网点被砸"],
                risk_level="critical",
                weight=5,
                suggested_tags=["突发事件", "运营风险"],
                description="监测银行运营相关突发公共事件",
                is_enabled=1,
            ),
        ]

        db.add_all(rules_a + rules_b)
        db.flush()

        sample_events = [
            {
                "project_id": project_a.id,
                "title": "网传某景区宰客严重，游客被强制消费5000元",
                "content": "今日某论坛网友爆料，其在某景区旅游时被导游强制带到购物点消费，不消费不让离开，最终被迫消费5000元购买劣质玉器。已有多名跟团游客反映类似情况，希望文旅局严查。",
                "source_url": "https://bbs.example.com/thread-12345.html",
                "source_type": "论坛",
                "author": "愤怒的游客",
                "forward_count": 120,
                "comment_count": 85,
                "like_count": 45,
                "read_count": 8500,
            },
            {
                "project_id": project_a.id,
                "title": "某景区发生山体滑坡，所幸无人员伤亡",
                "content": "今日下午，某市某景区后山突发山体滑坡，落石砸中景区游步道。景区管理方第一时间疏散游客，目前未收到人员伤亡报告，景区已临时闭园排查安全隐患。",
                "source_url": "https://news.example.com/local/20260619/001.html",
                "source_type": "新闻网站",
                "author": "本地新闻",
                "forward_count": 800,
                "comment_count": 320,
                "like_count": 150,
                "read_count": 52000,
            },
            {
                "project_id": project_b.id,
                "title": "某银行APP今日上午出现大面积登录失败",
                "content": "多名网友反映某银行APP从今日9点开始出现大面积无法登录的情况，转账、查询等功能均无法使用。客服回应称正在紧急抢修，预计2小时内恢复。",
                "source_url": "https://weibo.com/example/123456789",
                "source_type": "微博",
                "author": "科技数码君",
                "forward_count": 2500,
                "comment_count": 1200,
                "like_count": 800,
                "read_count": 250000,
            },
            {
                "project_id": project_b.id,
                "title": "正常理财科普：如何辨别正规银行理财产品",
                "content": "今天给大家科普一下如何辨别正规的银行理财产品，主要看三个方面：产品备案号、风险等级提示、销售渠道。大家有疑问可以在评论区留言。",
                "source_url": "https://zhihu.com/question/123456",
                "source_type": "问答社区",
                "author": "金融科普达人",
                "forward_count": 5,
                "comment_count": 12,
                "like_count": 80,
                "read_count": 3200,
            },
        ]

        for se in sample_events:
            project = db.query(Project).filter(Project.id == se["project_id"]).first()
            rules = (
                db.query(WarningRule)
                .filter(
                    WarningRule.project_id == se["project_id"],
                    WarningRule.is_enabled == 1,
                )
                .all()
            )
            full_text = f"{se['title']}\n{se['content']}"
            assessment, propagation_score = risk_engine.assess(
                text=full_text,
                rules=rules,
                key_entities=project.key_entities,
                forward_count=se["forward_count"],
                comment_count=se["comment_count"],
                like_count=se["like_count"],
                read_count=se["read_count"],
            )
            event = WarningEvent(
                project_id=se["project_id"],
                title=se["title"],
                content=se["content"],
                source_url=se["source_url"],
                source_type=se["source_type"],
                author=se["author"],
                forward_count=se["forward_count"],
                comment_count=se["comment_count"],
                like_count=se["like_count"],
                read_count=se["read_count"],
                propagation_score=propagation_score,
                risk_level=assessment.risk_level,
                hit_reasons=assessment.hit_reasons,
                suggested_tags=assessment.suggested_tags,
                matched_rules=assessment.matched_rules,
                need_manual_review=1 if assessment.need_manual_review else 0,
                status=EVENT_STATUS_PENDING,
            )
            db.add(event)

        db.commit()
        print("示例数据初始化完成！")
        print(f"  项目数量: {db.query(Project).count()}")
        print(f"  规则数量: {db.query(WarningRule).count()}")
        print(f"  事件数量: {db.query(WarningEvent).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_sample_data()
