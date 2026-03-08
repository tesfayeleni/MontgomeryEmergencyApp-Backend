import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.signal import RealTimeSignal, SignalType
from app.models.zone import Zone
from app.models.risk import RiskScore
import hashlib


class SignalFusionAgent:
    """
    Monitors news signals and updates zone-level signal multipliers.

    ZONE ROUTING FIX:
    - Old behaviour: unmatched signals defaulted to zone_map[0] (always Downtown)
    - New behaviour: unmatched signals are distributed round-robin across all zones
      so no single zone gets artificially inflated signal counts
    """

    def __init__(self, db: Session):
        self.db = db
        self.rss_feeds = [
            "https://news.google.com/rss/search?q=Montgomery%20Alabama",
        ]
        self._round_robin_index = 0

    # ── Street / keyword → zone mapping ──────────────────────────────
    STREET_MAPPINGS = {
        "westside": [
            "rosa parks", "rosa l parks", "west boulevard", "west blvd",
            "mobile highway", "mobile hwy", "west side", "westside",
            "berwick", "lynwood", "w south blvd", "w. south",
            "speigle", "ann st", "ann street",
        ],
        "eastside": [
            "eastern blvd", "eastern boulevard", "eastern bypass",
            "taylor road", "taylor rd", "norman bridge",
            "east boulevard", "east blvd", "east side", "eastside",
            "bell rd", "bell road", "carmichael", "biltmore",
            "university dr", "university drive",
        ],
        "northside": [
            "northern blvd", "north boulevard", "north blvd",
            "north side", "northside", "north montgomery",
            "wetumpka", "ray thorington", "lower wetumpka",
            "twin lakes", "air base", "lagoon park",
        ],
        "downtown": [
            "downtown", "midtown", "court square",
            "dexter ave", "dexter avenue", "commerce st", "commerce street",
            "main st", "main street", "monroe st", "ripley",
            "molton st", "lee st", "railroad st", "dexter plaza",
            "montgomery street", "madison av",
        ],
    }

    # High-severity keywords that should raise severity regardless of zone
    HIGH_KEYWORDS    = ["shooting", "shot", "fire", "explosion", "stabbing",
                        "homicide", "murder", "emergency", "critical", "crash", "dead"]
    MEDIUM_KEYWORDS  = ["accident", "incident", "alert", "warning", "arrest",
                        "robbery", "burglary", "assault", "theft", "missing"]

    def fetch_rss_signals(self) -> List[Dict]:
        signals = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:15]:
                    signals.append({
                        "title":       entry.get("title", ""),
                        "description": entry.get("summary", ""),
                        "link":        entry.get("link", ""),
                        "timestamp":   datetime.utcnow(),
                    })
            except Exception as e:
                print(f"RSS fetch error {feed_url}: {e}")
        return signals

    def extract_zone_mentions(self, text: str, signal_index: int, total_zones: int) -> List[str]:
        """
        Returns matched zone names from text.
        If no match found, distributes to a zone via round-robin instead of
        always defaulting to Downtown.
        """
        lower = text.lower()
        matched = []

        for zone_name, keywords in self.STREET_MAPPINGS.items():
            for kw in keywords:
                if kw in lower:
                    if zone_name not in matched:
                        matched.append(zone_name)
                    break

        if matched:
            return matched

        # Round-robin fallback — distribute evenly across zones
        zone_names = list(self.STREET_MAPPINGS.keys())
        fallback = zone_names[signal_index % total_zones]
        return [fallback]

    def classify_severity(self, text: str) -> str:
        lower = text.lower()
        if any(kw in lower for kw in self.HIGH_KEYWORDS):
            return "high"
        elif any(kw in lower for kw in self.MEDIUM_KEYWORDS):
            return "medium"
        return "low"

    def calculate_signal_weight(self, severity: str, recency_hours: int = 1) -> float:
        severity_map = {"low": 0.3, "medium": 0.6, "high": 1.0}
        recency_decay = max(0.1, 1.0 - (recency_hours / 48.0))
        return severity_map.get(severity, 0.3) * recency_decay
    
    def run(self):
        self.db.expire_all()  # force fresh zone data, clears 2.4hr stale cache
    
        try:
            signals = self.fetch_rss_signals()
            zones = self.db.query(Zone).all()
            zone_map = {z.name.lower(): z for z in zones}
            n_zones = len(zones)
    
            print(f"SignalFusionAgent: {len(signals)} signals fetched, {n_zones} zones loaded", flush=True)
    
            for idx, signal in enumerate(signals):
                full_text = signal["title"] + " " + signal["description"]
                severity = self.classify_severity(full_text)
                zone_names = self.extract_zone_mentions(full_text, idx, n_zones)
    
                for zone_name in zone_names:
                    zone = zone_map.get(zone_name.lower())
                    if not zone:
                        continue
    
                    title_hash = hashlib.md5(signal["title"].encode()).hexdigest()[:8]
                    sig_id = f"sig_{zone.id}_{title_hash}"
    
                    exists = self.db.query(RealTimeSignal).filter(
                        RealTimeSignal.id == sig_id,
                        RealTimeSignal.ex

    def update_signal_multipliers(self):
        zones = self.db.query(Zone).all()

        for zone in zones:
            active_signals = self.db.query(RealTimeSignal).filter(
                RealTimeSignal.zone_id == zone.id,
                RealTimeSignal.expires_at > datetime.utcnow(),
            ).all()

            if active_signals:
                weights     = [s.weight for s in active_signals]
                multiplier  = 1.0 + sum(weights) * 0.2
                multiplier  = min(3.0, multiplier)
            else:
                multiplier = 1.0

            risk_score = self.db.query(RiskScore).filter(
                RiskScore.zone_id == zone.id
            ).first()

            if risk_score:
                risk_score.signal_multiplier = round(multiplier, 4)

        self.db.commit()
