from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

from app.models.rule import (
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
)
from app.schemas.event import RiskAssessmentResult


RISK_LEVEL_ORDER = {
    RISK_LEVEL_LOW: 1,
    RISK_LEVEL_MEDIUM: 2,
    RISK_LEVEL_HIGH: 3,
    RISK_LEVEL_CRITICAL: 4,
}

RISK_LEVEL_WEIGHTS = {
    RISK_LEVEL_LOW: 1,
    RISK_LEVEL_MEDIUM: 3,
    RISK_LEVEL_HIGH: 6,
    RISK_LEVEL_CRITICAL: 10,
}

PROPAGATION_THRESHOLDS = {
    "high_engagement": 1000,
    "medium_engagement": 100,
}

MANUAL_REVIEW_TRIGGERS = {
    "critical_rule_hit": True,
    "multiple_rules_hit": 3,
    "high_propagation": 5000,
    "combined_score": 15,
}


@dataclass
class MatchedRule:
    rule_id: int
    rule_name: str
    rule_type: str
    risk_level: str
    weight: int
    matched_keywords: List[str] = field(default_factory=list)
    keyword_hit_count: int = 0


class RiskAssessmentEngine:
    def __init__(self):
        pass

    def _calculate_propagation_score(
        self,
        forward_count: int = 0,
        comment_count: int = 0,
        like_count: int = 0,
        read_count: int = 0,
    ) -> float:
        score = (
            forward_count * 1.5
            + comment_count * 1.2
            + like_count * 0.3
            + read_count * 0.05
        )
        return round(score, 2)

    def _match_keywords(self, text: str, keywords: List[str]) -> List[str]:
        matched = []
        text_lower = text.lower()
        for kw in keywords:
            if kw and kw.lower() in text_lower:
                matched.append(kw)
        return matched

    def _match_rules(
        self,
        text: str,
        rules: List,
    ) -> List[MatchedRule]:
        matched_rules = []
        for rule in rules:
            if not rule.is_enabled:
                continue
            matched_keywords = self._match_keywords(text, rule.keywords or [])
            if matched_keywords:
                matched_rules.append(
                    MatchedRule(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        rule_type=rule.rule_type,
                        risk_level=rule.risk_level,
                        weight=rule.weight,
                        matched_keywords=matched_keywords,
                        keyword_hit_count=len(matched_keywords),
                    )
                )
        return matched_rules

    def _determine_overall_risk(
        self, matched_rules: List[MatchedRule], propagation_score: float
    ) -> str:
        if not matched_rules:
            return RISK_LEVEL_LOW

        max_level = RISK_LEVEL_LOW
        total_weighted_score = 0.0

        for mr in matched_rules:
            if RISK_LEVEL_ORDER[mr.risk_level] > RISK_LEVEL_ORDER[max_level]:
                max_level = mr.risk_level
            base_score = RISK_LEVEL_WEIGHTS.get(mr.risk_level, 1)
            total_weighted_score += base_score * mr.weight * mr.keyword_hit_count

        total_weighted_score += propagation_score * 0.001

        if total_weighted_score >= 30 or max_level == RISK_LEVEL_CRITICAL:
            return RISK_LEVEL_CRITICAL
        elif total_weighted_score >= 15 or max_level == RISK_LEVEL_HIGH:
            return RISK_LEVEL_HIGH
        elif total_weighted_score >= 5 or max_level == RISK_LEVEL_MEDIUM:
            return RISK_LEVEL_MEDIUM
        else:
            return RISK_LEVEL_LOW

    def _generate_hit_reasons(
        self, matched_rules: List[MatchedRule], key_entities: Optional[List[str]] = None
    ) -> List[str]:
        reasons = []
        for mr in matched_rules:
            type_desc = {
                "policy_dispute": "政策争议类",
                "leader_related": "领导干部关联类",
                "governance_complaint": "基层治理投诉类",
                "public_emergency": "突发公共事件类",
                "custom": "自定义规则类",
            }.get(mr.rule_type, "其他")

            kw_str = "、".join(mr.matched_keywords)
            reasons.append(f"命中{type_desc}规则[{mr.rule_name}]，关键词：{kw_str}")

        if key_entities:
            pass

        return reasons

    def _collect_suggested_tags(
        self, matched_rules: List[MatchedRule], rule_models: List
    ) -> List[str]:
        tags = set()
        rule_id_to_model = {r.id: r for r in rule_models}

        for mr in matched_rules:
            rule = rule_id_to_model.get(mr.rule_id)
            if rule and rule.suggested_tags:
                for tag in rule.suggested_tags:
                    tags.add(tag)

            type_tags = {
                "policy_dispute": "政策争议",
                "leader_related": "领导干部",
                "governance_complaint": "基层治理",
                "public_emergency": "突发事件",
                "custom": "自定义敏感",
            }
            if mr.rule_type in type_tags:
                tags.add(type_tags[mr.rule_type])

        return sorted(list(tags))

    def _should_manual_review(
        self,
        matched_rules: List[MatchedRule],
        overall_risk: str,
        propagation_score: float,
        total_interactions: int,
    ) -> bool:
        if overall_risk == RISK_LEVEL_CRITICAL:
            return True

        if len(matched_rules) >= MANUAL_REVIEW_TRIGGERS["multiple_rules_hit"]:
            return True

        if total_interactions >= MANUAL_REVIEW_TRIGGERS["high_propagation"]:
            return True

        combined_score = sum(
            RISK_LEVEL_WEIGHTS.get(mr.risk_level, 1) * mr.weight * mr.keyword_hit_count
            for mr in matched_rules
        )
        if combined_score >= MANUAL_REVIEW_TRIGGERS["combined_score"]:
            return True

        return False

    def assess(
        self,
        text: str,
        rules: List,
        key_entities: Optional[List[str]] = None,
        forward_count: int = 0,
        comment_count: int = 0,
        like_count: int = 0,
        read_count: int = 0,
    ) -> Tuple[RiskAssessmentResult, float]:
        propagation_score = self._calculate_propagation_score(
            forward_count, comment_count, like_count, read_count
        )

        matched_rules = self._match_rules(text, rules)

        overall_risk = self._determine_overall_risk(matched_rules, propagation_score)

        hit_reasons = self._generate_hit_reasons(matched_rules, key_entities)

        suggested_tags = self._collect_suggested_tags(matched_rules, rules)

        total_interactions = forward_count + comment_count + like_count + read_count
        need_manual_review = self._should_manual_review(
            matched_rules, overall_risk, propagation_score, total_interactions
        )

        matched_rules_serializable = [
            {
                "rule_id": mr.rule_id,
                "rule_name": mr.rule_name,
                "rule_type": mr.rule_type,
                "risk_level": mr.risk_level,
                "weight": mr.weight,
                "matched_keywords": mr.matched_keywords,
                "keyword_hit_count": mr.keyword_hit_count,
            }
            for mr in matched_rules
        ]

        result = RiskAssessmentResult(
            risk_level=overall_risk,
            hit_reasons=hit_reasons,
            suggested_tags=suggested_tags,
            matched_rules=matched_rules_serializable,
            need_manual_review=need_manual_review,
        )

        return result, propagation_score


risk_engine = RiskAssessmentEngine()
