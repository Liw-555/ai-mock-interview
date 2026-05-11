"""
Multi-position scoring logic.
Supports position-specific dimension weights and score calculation.
"""

from typing import Dict, Any, Optional

from services.prompt_selector import POSITION_DIMENSIONS


# Legacy PM-only weights (kept for backward compatibility)
DIMENSION_WEIGHTS = {
    "product_thinking": 0.20,
    "data_ability": 0.20,
    "project_depth": 0.25,
    "expression_logic": 0.20,
    "business_understanding": 0.15,
}


def get_dimension_weights(category: str = "pm") -> Dict[str, float]:
    """
    Get dimension weights for a position category.
    Falls back to PM weights if category is unknown.
    """
    dims = POSITION_DIMENSIONS.get(category, POSITION_DIMENSIONS["pm"])
    return {dim_key: dim_info["weight"] for dim_key, dim_info in dims.items()}


def calculate_total_score(dimensions: Dict[str, int], category: str = "pm") -> int:
    """
    Calculate total score from dimension scores using position-specific weights.
    total_score = weighted_avg * 20, max 100.
    """
    weights = get_dimension_weights(category)
    total = 0.0
    for dim, weight in weights.items():
        score = dimensions.get(dim, 3)
        total += score * weight
    return int(round(total * 20))


def get_dimension_names(category: str = "pm") -> Dict[str, str]:
    """
    Get dimension key -> Chinese name mapping for a position category.
    """
    dims = POSITION_DIMENSIONS.get(category, POSITION_DIMENSIONS["pm"])
    return {dim_key: dim_info["name"] for dim_key, dim_info in dims.items()}


def get_empty_score(category: str = "pm") -> dict:
    """
    Get an empty score dict with all dimensions set to 0 for a position category.
    """
    dims = POSITION_DIMENSIONS.get(category, POSITION_DIMENSIONS["pm"])
    result = {"total_score": 0}
    for dim_key in dims:
        result[dim_key] = 0
    result["per_question"] = []
    result["improvement_suggestions"] = []
    result["reference_answers"] = []
    return result
