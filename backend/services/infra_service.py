"""
SENTINEL Intel — Infrastructure OSINT Service
Domain intelligence gathering via WHOIS, DNS, and certificate transparency.
"""
from __future__ import annotations
import re
from urllib.parse import urlparse


def extract_domains_from_results(results: list[dict]) -> list[str]:
    """Extract unique domains from search results."""
    domains = set()
    for r in results:
        url = r.get("url", "")
        if url:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower().replace("www.", "")
                if domain and "." in domain:
                    domains.add(domain)
            except Exception:
                pass
    return sorted(domains)


def analyze_domain(domain: str) -> dict:
    """
    Analyze a domain's infrastructure.
    Uses publicly available data — WHOIS, DNS lookups.
    External API integrations (Shodan, URLScan, crt.sh) require API keys.
    """
    intel = {
        "domain": domain,
        "registrar": "",
        "registrant_country": "",
        "registration_date": "",
        "privacy_shield": False,
        "hosting_provider": "",
        "hosting_country": "",
        "ip_address": "",
        "asn": "",
        "ssl_issuer": "",
        "ssl_certs_count": 0,
        "open_ports": [],
        "technologies": [],
        "related_domains": [],
    }

    # WHOIS lookup (best-effort)
    try:
        import whois
        w = whois.whois(domain)
        intel["registrar"] = str(w.registrar or "")
        if w.creation_date:
            date = w.creation_date
            if isinstance(date, list):
                date = date[0]
            intel["registration_date"] = str(date)[:10]
        if w.country:
            intel["registrant_country"] = str(w.country)
        if w.registrant_country:
            intel["registrant_country"] = str(w.registrant_country)
        # Detect privacy shields
        registrant = str(w.org or w.name or "").lower()
        privacy_keywords = ["privacy", "proxy", "whoisguard", "domains by proxy", "redacted", "contact privacy"]
        intel["privacy_shield"] = any(k in registrant for k in privacy_keywords)
    except Exception:
        pass

    # DNS/IP resolution
    try:
        import socket
        ip = socket.gethostbyname(domain)
        intel["ip_address"] = ip
    except Exception:
        pass

    # IP geolocation (free API, best-effort)
    if intel["ip_address"]:
        try:
            import requests
            # Using ip-api.com free endpoint for all IP data
            resp = requests.get(f"http://ip-api.com/json/{intel['ip_address']}?fields=status,country,isp,as,org,city", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    intel["hosting_country"] = data.get("country", "")
                    intel["hosting_provider"] = data.get("isp", "")
                    intel["asn"] = data.get("as", "")
                    
                    # We can also add some additional info to technologies
                    org = data.get("org", "")
                    if org:
                        intel["technologies"].append(f"Hosted by: {org}")
        except Exception:
            pass

    return intel


def find_shared_infrastructure(domain_intels: list[dict]) -> list[list[str]]:
    """Find domains sharing the same infrastructure (IP subnet, hosting provider, registrar)."""
    clusters = []

    # Group by /24 subnet
    subnet_map: dict[str, list[str]] = {}
    for d in domain_intels:
        ip = d.get("ip_address", "")
        if ip:
            subnet = ".".join(ip.split(".")[:3])
            subnet_map.setdefault(subnet, []).append(d["domain"])

    for subnet, domains in subnet_map.items():
        if len(domains) > 1:
            clusters.append(domains)

    return clusters


def analyze_domains_batch(results: list[dict]) -> dict:
    """Analyze all domains found in results."""
    domains = extract_domains_from_results(results)[:20]  # Cap at 20 to avoid long runs
    intels = []
    for domain in domains:
        intel = analyze_domain(domain)
        intels.append(intel)

    clusters = find_shared_infrastructure(intels)

    return {
        "domains_analyzed": len(intels),
        "shared_infrastructure_clusters": len(clusters),
        "domains": intels,
        "clusters": clusters,
    }
