"""
llm_alerts.py — LLM-powered alert generation

Replaces rule-based alert strings with Claude-generated natural language.
Claude receives structured zone risk data and produces:
- A concise situation summary per high-risk zone
- A specific recommended action (not just "pre-position resources")
- A confidence qualifier based on data volume

This is what makes the alerts genuinely "AI-generated" rather than
template-filled strings.
"""

import os
import requests
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"


def generate_zone_alerts(risk_scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes risk score data for all zones and returns LLM-generated alerts
    for zones that need attention.

    Falls back to rule-based alerts if API key not set or call fails.
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("[LLM] No ANTHROPIC_API_KEY — using rule-based fallback")
        return _rule_based_fallback(risk_scores)

    # Only send zones that warrant an alert (score > 30) to save tokens
    alert_zones = [z for z in risk_scores if z.get("final_risk_score", 0) > 30]

    if not alert_zones:
        return [{
            "severity": "info",
            "message":  "All zones within normal parameters. No immediate action required.",
            "zone":     "All Zones",
        }]

    prompt = _build_prompt(alert_zones, risk_scores)

    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",  # Fast + cheap for alerts
                "max_tokens": 800,
                "messages": [{
                    "role":    "user",
                    "content": prompt,
                }],
            },
            timeout=15,
        )
        response.raise_for_status()
        raw = response.json()["content"][0]["text"]

        # Parse JSON response from Claude
        alerts = _parse_llm_response(raw)
        logger.info(f"[LLM] Generated {len(alerts)} alerts")
        return alerts

    except Exception as e:
        logger.error(f"[LLM] Alert generation failed: {e} — using fallback")
        return _rule_based_fallback(risk_scores)


def _build_prompt(alert_zones: List[Dict], all_zones: List[Dict]) -> str:
    now = datetime.utcnow().strftime("%A %I:%M %p UTC")

    zone_summary = "\n".join([
        f"- {z['zone_name']}: risk={z['final_risk_score']:.1f}/100, "
        f"police_demand={z['predicted_demand_police']:.1f} vs capacity={z['effective_capacity_police']}, "
        f"fire_demand={z['predicted_demand_fire']:.1f} vs capacity={z['effective_capacity_fire']}, "
        f"signal_multiplier={z['signal_multiplier']:.2f} "
        f"({'rising' if z['signal_multiplier'] > 1.5 else 'stable'})"
        for z in alert_zones
    ])

    all_zone_names = [z["zone_name"] for z in all_zones]

    return f"""You are an AI system for Montgomery, Alabama Emergency Management.
Current time: {now}
City zones: {', '.join(all_zone_names)}

Zone risk data requiring attention:
{zone_summary}

Generate emergency management alerts. For each zone above, produce one alert with:
1. A specific, actionable recommendation (name actual station types, not just "resources")
2. The reason based on the data (demand vs capacity ratio, signal activity)
3. A severity: "critical" (score>80), "high" (score>60), "warning" (score>30)

Respond ONLY with valid JSON array, no markdown, no explanation:
[
  {{
    "zone": "zone name",
    "severity": "critical|high|warning",
    "message": "2-3 sentence alert with specific recommendation"
  }}
]

Be direct and specific. Example of good message: "Westside demand is approaching police capacity with signal activity rising. Historical Friday evening patterns suggest incident spike likely within 2-3 hours. Recommend pre-positioning one additional police unit from Northside to Westside Station 1."
"""


def _parse_llm_response(raw: str) -> List[Dict]:
    """Parse Claude's JSON response, handle minor formatting issues."""
    try:
        # Strip any accidental markdown fences
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        alerts = json.loads(clean)
        if isinstance(alerts, list):
            return alerts
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"[LLM] JSON parse failed: {e} — raw: {raw[:200]}")

    return _rule_based_fallback([])


def _rule_based_fallback(risk_scores: List[Dict]) -> List[Dict]:
    """Simple rule-based alerts used when LLM is unavailable."""
    alerts = []
    for z in risk_scores:
        score = z.get("final_risk_score", 0)
        name  = z.get("zone_name", "Unknown")
        sigs  = z.get("active_high_signals", 0)
        sig_text = (
            f"{sigs} active high-severity signals."
            if sigs > 0
            else "Elevated historical incident rate."
        )

        if score > 80:
            alerts.append({
                "zone":     name,
                "severity": "critical",
                "message":  f"URGENT: {name} — risk score {score:.1f}. {sig_text} Recommend pre-positioning resources.",
            })
        elif score > 60:
            alerts.append({
                "zone":     name,
                "severity": "high",
                "message":  f"WARNING: {name} — risk score {score:.1f}. {sig_text} Monitor closely.",
            })
        elif z.get("signal_multiplier", 1) > 2:
            alerts.append({
                "zone":     name,
                "severity": "warning",
                "message":  f"ESCALATING: {name} signal activity surging — monitor closely.",
            })

    if not alerts:
        alerts.append({
            "zone":     "All Zones",
            "severity": "info",
            "message":  "All zones within normal parameters.",
        })

    return alerts