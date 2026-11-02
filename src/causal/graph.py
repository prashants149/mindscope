"""
Structural Causal Graph (DAG) specification for MindScope.
Defines causal relationships between academic/lifestyle stressors, depression,
and downstream academic outcomes.
"""

from typing import Dict, Any


def get_causal_dag_dot() -> str:
    """
    Returns DOT string representation of the Structural Causal Graph.
    Nodes:
      - Exogenous Demographics: age, gender
      - Stressors & Coping: financial_stress, social_support, academic_pressure, screen_time_hours, sleep_hours
      - Core Mediator: depression_score
      - Downstream Outcomes: attendance_rate, cgpa
    """
    return """
    digraph {
        financial_stress -> academic_pressure;
        financial_stress -> depression_score;
        social_support -> depression_score;
        social_support -> screen_time_hours;
        academic_pressure -> screen_time_hours;
        academic_pressure -> sleep_hours;
        academic_pressure -> depression_score;
        academic_pressure -> cgpa;
        screen_time_hours -> sleep_hours;
        screen_time_hours -> depression_score;
        sleep_hours -> depression_score;
        sleep_hours -> attendance_rate;
        depression_score -> attendance_rate;
        depression_score -> cgpa;
        age -> academic_pressure;
        age -> sleep_hours;
        gender -> depression_score;
    }
    """.strip()


def get_causal_dag_gml() -> str:
    """
    Returns GML representation for DoWhy compatibility.
    """
    return """graph[
        node[id "age" label "age"]
        node[id "gender" label "gender"]
        node[id "financial_stress" label "financial_stress"]
        node[id "social_support" label "social_support"]
        node[id "academic_pressure" label "academic_pressure"]
        node[id "screen_time_hours" label "screen_time_hours"]
        node[id "sleep_hours" label "sleep_hours"]
        node[id "depression_score" label "depression_score"]
        node[id "attendance_rate" label "attendance_rate"]
        node[id "cgpa" label "cgpa"]
        edge[source "financial_stress" target "academic_pressure"]
        edge[source "financial_stress" target "depression_score"]
        edge[source "social_support" target "depression_score"]
        edge[source "social_support" target "screen_time_hours"]
        edge[source "academic_pressure" target "screen_time_hours"]
        edge[source "academic_pressure" target "sleep_hours"]
        edge[source "academic_pressure" target "depression_score"]
        edge[source "academic_pressure" target "cgpa"]
        edge[source "screen_time_hours" target "sleep_hours"]
        edge[source "screen_time_hours" target "depression_score"]
        edge[source "sleep_hours" target "depression_score"]
        edge[source "sleep_hours" target "attendance_rate"]
        edge[source "depression_score" target "attendance_rate"]
        edge[source "depression_score" target "cgpa"]
        edge[source "age" target "academic_pressure"]
        edge[source "age" target "sleep_hours"]
        edge[source "gender" target "depression_score"]
    ]"""
