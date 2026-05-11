"""
Prompt selector: selects the appropriate interview prompt template
based on the job position category and interview round.

Position categories:
  - pm (产品经理): default
  - ops (运营)
  - da (数据分析)
  - algo (算法工程师)
  - dev (研发工程师)
"""

from typing import Tuple, Dict, Any

# Position category detection keywords
CATEGORY_KEYWORDS = {
    "pm": ["产品经理", "产品", "pm", "product manager", "产品策划", "产品规划"],
    "ops": ["运营", "产品运营", "用户运营", "内容运营", "活动运营", "ops", "operation"],
    "da": ["数据分析", "数据分析师", "data analyst", "data analysis", "商业分析", "bi", "business intelligence"],
    "algo": ["算法", "算法工程师", "algorithm", "ml", "machine learning", "ai工程师", "nlp", "cv", "推荐算法", "搜索算法"],
    "dev": ["研发", "开发", "后端", "前端", "全栈", "软件工程师", "developer", "engineer", "swe", "测试开发", "大数据开发", "java", "go", "python开发"],
}

# Scoring dimensions per position category
POSITION_DIMENSIONS = {
    "pm": {
        "product_thinking": {"name": "产品思维", "weight": 0.20},
        "data_ability": {"name": "数据能力", "weight": 0.20},
        "project_depth": {"name": "项目深度", "weight": 0.25},
        "expression_logic": {"name": "表达逻辑", "weight": 0.20},
        "business_understanding": {"name": "业务理解", "weight": 0.15},
    },
    "ops": {
        "ops_thinking": {"name": "运营思维", "weight": 0.20},
        "data_ability": {"name": "数据分析", "weight": 0.15},
        "plan_design": {"name": "方案设计", "weight": 0.25},
        "content_creativity": {"name": "内容创意", "weight": 0.15},
        "execution": {"name": "执行落地", "weight": 0.25},
    },
    "da": {
        "sql_ability": {"name": "SQL能力", "weight": 0.20},
        "statistics": {"name": "统计分析", "weight": 0.20},
        "business_insight": {"name": "业务洞察", "weight": 0.20},
        "model_application": {"name": "模型应用", "weight": 0.20},
        "communication": {"name": "沟通表达", "weight": 0.20},
    },
    "algo": {
        "algorithm_fundamentals": {"name": "算法基础", "weight": 0.20},
        "engineering_ability": {"name": "工程能力", "weight": 0.20},
        "project_depth": {"name": "项目深度", "weight": 0.25},
        "system_design": {"name": "系统设计", "weight": 0.20},
        "expression_ability": {"name": "表达能力", "weight": 0.15},
    },
    "dev": {
        "coding_ability": {"name": "代码能力", "weight": 0.20},
        "system_design": {"name": "系统设计", "weight": 0.20},
        "tech_depth": {"name": "技术深度", "weight": 0.20},
        "project_experience": {"name": "项目经验", "weight": 0.25},
        "collaboration": {"name": "协作沟通", "weight": 0.15},
    },
}

# Scoring rubric per position category
POSITION_RUBRICS = {
    "pm": {
        "product_thinking": {
            1: "无法区分真伪需求",
            2: "有基本产品意识",
            3: "能用框架分析需求",
            4: "能独立设计产品方案",
            5: "有创新的产品洞察",
        },
        "data_ability": {
            1: "不懂关键指标含义",
            2: "知道常见指标",
            3: "能选指标做分析",
            4: "能设计AB实验验证",
            5: "能用数据驱动决策闭环",
        },
        "project_depth": {
            1: "无法讲清项目细节",
            2: "能讲清做了什么",
            3: "能讲清为什么做",
            4: "能复盘决策逻辑",
            5: "能提炼方法论",
        },
        "expression_logic": {
            1: "回答无结构",
            2: "有基本逻辑",
            3: "能用STAR法则",
            4: "结论先行分点论证",
            5: "金字塔原理熟练运用",
        },
        "business_understanding": {
            1: "不了解行业基本概念",
            2: "知道行业大趋势",
            3: "理解公司核心业务",
            4: "能分析竞品差异",
            5: "能提出业务增长建议",
        },
    },
    "ops": {
        "ops_thinking": {
            1: "对运营无基本认知",
            2: "了解运营基础概念",
            3: "能运用AARRR等框架分析",
            4: "能独立设计运营方案",
            5: "有创新的运营洞察和增长方法论",
        },
        "data_ability": {
            1: "不关注数据",
            2: "知道看关键指标",
            3: "能用数据辅助决策",
            4: "能设计数据驱动的运营策略",
            5: "能建立数据监控体系并持续优化",
        },
        "plan_design": {
            1: "无法完成方案设计",
            2: "能写出基本方案框架",
            3: "方案逻辑完整可执行",
            4: "方案有创意且可衡量效果",
            5: "方案兼具创意、落地性和可扩展性",
        },
        "content_creativity": {
            1: "缺乏创意和文案能力",
            2: "能完成基本内容产出",
            3: "内容有针对性且形式多样",
            4: "能策划传播性强的内容",
            5: "能持续产出爆款内容并形成体系",
        },
        "execution": {
            1: "方案无法落地",
            2: "能按计划执行基本任务",
            3: "能把控项目节奏和关键节点",
            4: "能灵活应对突发问题并调整策略",
            5: "能从0到1搭建运营体系并持续迭代",
        },
    },
    "da": {
        "sql_ability": {
            1: "无法写基本查询",
            2: "掌握基本SELECT/JOIN",
            3: "能使用窗口函数和子查询",
            4: "能写复杂SQL解决业务问题",
            5: "精通SQL优化和性能调优",
        },
        "statistics": {
            1: "不了解基本统计概念",
            2: "了解描述性统计",
            3: "掌握假设检验和显著性检验",
            4: "能设计AB测试并计算样本量",
            5: "能运用因果推断解决复杂业务问题",
        },
        "business_insight": {
            1: "不关注业务背景",
            2: "了解基本业务指标",
            3: "能从数据中发现业务问题",
            4: "能提出可落地的业务建议",
            5: "能建立完整的指标体系驱动业务增长",
        },
        "model_application": {
            1: "不了解机器学习基础",
            2: "了解常见算法概念",
            3: "能选择合适算法解决业务问题",
            4: "能优化模型并解释结果",
            5: "能端到端构建ML解决方案并持续迭代",
        },
        "communication": {
            1: "无法清晰表达分析结论",
            2: "能说明数据结果",
            3: "能用可视化辅助说明",
            4: "能向非技术方清晰解释分析结论",
            5: "能用数据故事驱动业务决策",
        },
    },
    "algo": {
        "algorithm_fundamentals": {
            1: "无法写基本算法",
            2: "能解决简单编程题",
            3: "掌握常见数据结构和算法范式",
            4: "能设计高效算法并分析复杂度",
            5: "能解决竞赛级难题并优化到最优复杂度",
        },
        "engineering_ability": {
            1: "代码无法运行",
            2: "代码能跑但缺乏规范",
            3: "代码规范、有边界处理",
            4: "代码有测试用例和异常处理",
            5: "代码工程化程度高，可维护可扩展",
        },
        "project_depth": {
            1: "无法讲清项目细节",
            2: "能讲清做了什么",
            3: "能讲清为什么选这个方案",
            4: "能复盘指标提升的归因逻辑",
            5: "能提炼方法论并推广到其他场景",
        },
        "system_design": {
            1: "不了解系统设计基础",
            2: "了解常见架构组件",
            3: "能设计基本系统架构",
            4: "能处理高可用和扩展性问题",
            5: "能设计大规模分布式系统并权衡取舍",
        },
        "expression_ability": {
            1: "回答无条理",
            2: "有基本表达逻辑",
            3: "能用STAR-L框架回答",
            4: "技术讲解清晰易懂",
            5: "能深入浅出解释复杂概念",
        },
    },
    "dev": {
        "coding_ability": {
            1: "无法手写基本代码",
            2: "能写基本功能代码",
            3: "代码规范、有边界处理",
            4: "能写出高质量可维护代码",
            5: "代码优雅、高效、可扩展",
        },
        "system_design": {
            1: "无法设计基本系统",
            2: "了解常见架构模式",
            3: "能设计完整系统架构",
            4: "能处理高并发和高可用问题",
            5: "能设计大规模分布式系统并做技术选型权衡",
        },
        "tech_depth": {
            1: "对八股文概念不清晰",
            2: "了解常见技术概念",
            3: "能解释技术原理和底层机制",
            4: "能深入分析技术方案优劣",
            5: "精通底层原理并能给出优化方案",
        },
        "project_experience": {
            1: "无法讲清项目细节",
            2: "能讲清做了什么",
            3: "能讲清技术选型原因和架构设计",
            4: "能复盘项目难点和解决方案",
            5: "能提炼技术方法论并指导团队",
        },
        "collaboration": {
            1: "团队协作意识弱",
            2: "能配合团队完成工作",
            3: "能主动沟通解决技术分歧",
            4: "能推动跨团队技术协作",
            5: "能建立技术规范和流程提升团队效率",
        },
    },
}

# Suggestion texts per position category and dimension
POSITION_SUGGESTIONS = {
    "pm": {
        "product_thinking": "多阅读产品案例分析，练习从用户需求出发推导产品方案。",
        "data_ability": "学习常用的数据分析方法，面试中多用数据支撑观点。",
        "project_depth": "用STAR法则复盘过往项目，准备1-2个能深入展开的案例。",
        "expression_logic": "练习结构化表达（总-分-总），回答前先梳理关键要点。",
        "business_understanding": "深入了解目标公司的产品和商业模式，关注行业动态。",
    },
    "ops": {
        "ops_thinking": "学习AARRR、RFM等运营框架，练习用框架拆解运营问题。",
        "data_ability": "培养数据敏感度，面试中多用具体数据支撑运营决策。",
        "plan_design": "练习完整的运营方案设计：目标→用户→玩法→渠道→预算→评估。",
        "content_creativity": "关注爆款内容案例，积累不同类型的内容策划方法。",
        "execution": "用STAR法则复盘过往运营项目，重点展示落地能力和结果。",
    },
    "da": {
        "sql_ability": "刷LeetCode SQL题，重点练习窗口函数、自连接和复杂查询。",
        "statistics": "系统学习假设检验和AB测试设计，掌握样本量计算方法。",
        "business_insight": "练习指标异动归因分析，学习GMV拆解等业务分析框架。",
        "model_application": "深入理解常见ML算法原理，面试中能解释选型理由和优化方法。",
        "communication": "练习向非技术方解释分析结论，用数据故事驱动业务决策。",
    },
    "algo": {
        "algorithm_fundamentals": "持续刷LeetCode，重点练习动态规划和树/图问题，先讲思路再写代码。",
        "engineering_ability": "练习代码规范：边界处理、自测用例、异常处理、变量命名。",
        "project_depth": "用STAR-L框架复盘项目：背景→任务→行动→量化结果→学习反思。",
        "system_design": "学习推荐系统、大模型部署等系统设计，练习画架构图和权衡分析。",
        "expression_ability": "练习深入浅出地解释技术概念，面试中先讲思路再写代码。",
    },
    "dev": {
        "coding_ability": "刷LeetCode前200道easy+medium，练习手撕代码和边界处理。",
        "system_design": "学习常见系统设计题（IM、短链、评论系统），练习画架构图。",
        "tech_depth": "深入理解MySQL/Redis/Kafka底层原理，不止于八股文表面。",
        "project_experience": "用STAR法则复盘项目，重点讲技术选型原因和解决的技术难点。",
        "collaboration": "练习讲述跨团队协作案例，展示沟通推动和技术决策能力。",
    },
}


def detect_position_category(target_position: str, position_direction: str = None) -> str:
    """
    Detect the position category from target_position string and/or position_direction.
    Returns one of: 'pm', 'ops', 'da', 'algo', 'dev' (default: 'pm').
    """
    # Combine both fields for detection
    text = ""
    if position_direction:
        text += position_direction.lower() + " "
    if target_position:
        text += target_position.lower()

    if not text.strip():
        return "pm"  # default

    # Score each category by keyword matches
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[category] = score

    # Return the category with highest score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "pm"  # default if no keyword matches
    return best


def get_prompt_template(category: str, is_hr: bool = False) -> Tuple[str, dict]:
    """
    Get the appropriate prompt template and style descriptions for a position category.

    Args:
        category: Position category ('pm', 'ops', 'da', 'algo', 'dev')
        is_hr: Whether this is an HR round

    Returns:
        Tuple of (SYSTEM_PROMPT string, STYLE_DESCRIPTIONS dict)
    """
    if is_hr:
        template_map = {
            "pm": "prompts.pm_hr",
            "ops": "prompts.ops_hr",
            "da": "prompts.da_hr",
            "algo": "prompts.algo_hr",
            "dev": "prompts.dev_hr",
        }
    else:
        template_map = {
            "pm": "prompts.pm_round1",
            "ops": "prompts.ops_round1",
            "da": "prompts.da_round1",
            "algo": "prompts.algo_round1",
            "dev": "prompts.dev_round1",
        }

    module_path = template_map.get(category, template_map["pm"])

    import importlib
    module = importlib.import_module(module_path)
    return module.SYSTEM_PROMPT, module.STYLE_DESCRIPTIONS


def get_position_dimensions(category: str) -> Dict[str, Dict[str, Any]]:
    """
    Get scoring dimensions for a position category.

    Returns:
        Dict mapping dimension_key -> {"name": str, "weight": float}
    """
    return POSITION_DIMENSIONS.get(category, POSITION_DIMENSIONS["pm"])


def get_position_rubric(category: str) -> Dict[str, Dict[int, str]]:
    """
    Get scoring rubric for a position category.

    Returns:
        Dict mapping dimension_key -> {score_level: description}
    """
    return POSITION_RUBRICS.get(category, POSITION_RUBRICS["pm"])


def get_position_suggestions(category: str) -> Dict[str, str]:
    """
    Get improvement suggestion texts for a position category.

    Returns:
        Dict mapping dimension_key -> suggestion_text
    """
    return POSITION_SUGGESTIONS.get(category, POSITION_SUGGESTIONS["pm"])


def build_scoring_prompt(category: str, conversation_history: str, content_json: str) -> str:
    """
    Build a complete scoring prompt for the given position category.
    Uses position-specific dimensions, weights, and rubrics.
    """
    dimensions = get_position_dimensions(category)
    rubric = get_position_rubric(category)

    # Build dimension list with weights
    dim_lines = []
    for dim_key, dim_info in dimensions.items():
        weight_pct = int(dim_info["weight"] * 100)
        dim_lines.append(f"- {dim_info['name']}（{weight_pct}%）")

    # Build rubric text
    rubric_text = ""
    for dim_key, levels in rubric.items():
        dim_name = dimensions[dim_key]["name"]
        rubric_text += f"\n{dim_name}：\n"
        for score, desc in levels.items():
            rubric_text += f"- {score}分：{desc}\n"

    # Build dimension weights JSON
    weights_json = ", ".join(
        f'"{dim_key}": {dim_info["weight"]:.2f}'
        for dim_key, dim_info in dimensions.items()
    )

    # Build dimension score fields
    score_fields = ", ".join(f'"{dim_key}": 1-5' for dim_key in dimensions)

    prompt = f"""你是一位资深面试评估专家。请根据以下面试对话，对候选人进行 {len(dimensions)} 维评分。

【评分维度与权重】
{chr(10).join(dim_lines)}

【Rubric 标准】
{rubric_text}

【评分原则】
1. 每条评语必须引用用户的原话或摘要，不能泛泛而谈
2. 评分必须与 Rubric 中的等级描述一一对应
3. 总分 = Σ(维度得分 × 维度权重) × 4，满分 100
4. 针对最薄弱的 2-3 个维度给出具体可操作的改进建议
5. 对得分 <= 2 分的问题，提供参考高分答案（结合候选人简历场景）

【面试对话历史】
{conversation_history}

【候选人简历摘要】
{content_json}

【输出格式】
请严格输出以下 JSON 格式：
{{
  {score_fields},
  "total_score": 0-100,
  "dimension_weights": {{{weights_json}}},
  "per_question": [
    {{
      "question_id": "q1",
      "question_summary": "问题摘要",
      "scores": {{"expression_logic": 3}},
      "comment": "评语，必须引用用户原话",
      "user_quote": "用户原话摘要"
    }}
  ],
  "improvement_suggestions": [
    {{
      "dimension": "维度名称",
      "score": 3,
      "priority": "高",
      "suggestion": "具体建议内容"
    }}
  ],
  "reference_answers": [
    {{
      "question_id": "q2",
      "high_score_answer": "参考高分答案"
    }}
  ]
}}
"""
    return prompt
