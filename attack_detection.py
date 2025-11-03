import json
from typing import Dict, List, Tuple

class AttackDetector:
    """ML-based and rule-based attack detection system."""

    ATTACK_TYPES = [
        'Normal',
        'Malware',
        'Phishing',
        'DoS',
        'DDoS',
        'Man-in-the-Middle',
        'SQL Injection',
        'Cross-Site Scripting',
        'Social Engineering',
        'Zero-Day Exploit',
        'Insider Threat',
        'Spoofing / Password Attack'
    ]

    ATTACK_THRESHOLDS = {
        'rate': 5000,
        'synack': 200,
        'tcprtt': 1500,
        'dinpkt': 800,
        'sbytes': 90000,
        'dbytes': 1000,
        'dmean': 0.7,
        'smean': 0.3,
        'ackdat': 500,
    }

    SEVERITY_LEVELS = {
        'Critical': ['DDoS', 'Zero-Day Exploit'],
        'High': ['DoS', 'Malware', 'Phishing', 'Man-in-the-Middle', 'Insider Threat', 'Spoofing / Password Attack'],
        'Medium': ['SQL Injection', 'Cross-Site Scripting', 'Social Engineering'],
        'Low': ['Normal']
    }

    @staticmethod
    def detect_attack(params: Dict) -> Tuple[str, float, str, int, List[str]]:
        """
        Detect attack type using rule-based logic.

        Returns: (attack_type, confidence, severity, risk_score, indicators)
        """
        indicators = []
        risk_score = 0

        sbytes = params.get('sbytes', 0)
        dbytes = params.get('dbytes', 0)
        rate = params.get('rate', 0)
        dinpkt = params.get('dinpkt', 0)
        tcprtt = params.get('tcprtt', 0)
        synack = params.get('synack', 0)
        ackdat = params.get('ackdat', 0)
        smean = params.get('smean', 0)
        dmean = params.get('dmean', 0)

        # Calculate risk score
        if rate > AttackDetector.ATTACK_THRESHOLDS['rate']:
            risk_score += 25
            indicators.append('High traffic rate detected')

        if synack > AttackDetector.ATTACK_THRESHOLDS['synack']:
            risk_score += 20
            indicators.append('Multiple SYN-ACK packets')

        if tcprtt > AttackDetector.ATTACK_THRESHOLDS['tcprtt']:
            risk_score += 15
            indicators.append('High TCP round-trip time')

        if dinpkt > AttackDetector.ATTACK_THRESHOLDS['dinpkt']:
            risk_score += 15
            indicators.append('High destination input packets')

        if sbytes > AttackDetector.ATTACK_THRESHOLDS['sbytes']:
            risk_score += 20
            indicators.append('Abnormally high source bytes')

        if dbytes < AttackDetector.ATTACK_THRESHOLDS['dbytes'] and sbytes > 50000:
            risk_score += 10
            indicators.append('Minimal response from destination')

        if dmean > AttackDetector.ATTACK_THRESHOLDS['dmean']:
            risk_score += 10
            indicators.append('Destination entropy high')

        if smean < AttackDetector.ATTACK_THRESHOLDS['smean'] and dmean > 0.5:
            risk_score += 10
            indicators.append('Source entropy anomaly')

        if ackdat > AttackDetector.ATTACK_THRESHOLDS['ackdat']:
            risk_score += 15
            indicators.append('High ACK-DAT packets detected')

        risk_score = min(100, max(0, risk_score))

        # Rule-based attack type detection
        if rate > 5000 and synack > 200:
            return 'DDoS', 0.95, 'Critical', risk_score, indicators + ['Distributed attack pattern']

        if tcprtt > 1500 and dinpkt > 800:
            return 'DoS', 0.92, 'High', risk_score, indicators + ['Congestion pattern detected']

        if sbytes > 90000 and dbytes < 1000:
            return 'Malware', 0.88, 'High', risk_score, indicators + ['Possible data exfiltration']

        if dmean > 0.7 and smean < 0.3:
            return 'Phishing', 0.85, 'High', risk_score, indicators + ['Credential harvesting pattern']

        if ackdat > 500 and synack < 50 and rate > 3000:
            return 'Man-in-the-Middle', 0.82, 'High', risk_score, indicators + ['Possible session hijacking']

        if dinpkt > 1000 and tcprtt < 100 and rate > 4000:
            return 'SQL Injection', 0.79, 'Medium', risk_score, indicators + ['Database query manipulation']

        if smean > 0.8 and dmean > 0.8 and sbytes > 50000:
            return 'Cross-Site Scripting', 0.76, 'Medium', risk_score, indicators + ['Script injection pattern']

        if rate < 100 and tcprtt > 2000:
            return 'Social Engineering', 0.73, 'Medium', risk_score, indicators + ['Possible human interaction attack']

        if sbytes > 100000 and rate > 6000 and synack > 300:
            return 'Zero-Day Exploit', 0.89, 'Critical', risk_score, indicators + ['Unknown vulnerability pattern']

        if dmean < 0.2 and smean > 0.9 and ackdat > 300:
            return 'Insider Threat', 0.81, 'High', risk_score, indicators + ['Internal actor behavior']

        if synack > 400 or (rate > 2000 and tcprtt < 50):
            return 'Spoofing / Password Attack', 0.84, 'High', risk_score, indicators + ['Brute force attempt pattern']

        if not indicators:
            indicators = ['Normal traffic pattern', 'No malicious indicators detected']

        return 'Normal', 0.98, 'Low', risk_score, indicators

    @staticmethod
    def get_recommendations(attack_type: str) -> List[str]:
        """Get recommended actions for detected attack type."""
        recommendations = {
            'Normal': ['Monitor regularly', 'Continue normal operations'],
            'Malware': [
                'Run antivirus scan immediately',
                'Isolate device from network',
                'Check for unauthorized software',
                'Review recent file modifications',
            ],
            'Phishing': [
                'Review recent communications',
                'Change passwords immediately',
                'Enable two-factor authentication',
                'Check email forwarding rules',
            ],
            'DoS': [
                'Block suspicious source IPs',
                'Increase bandwidth capacity',
                'Enable rate limiting',
                'Contact ISP for mitigation',
            ],
            'DDoS': [
                'Activate DDoS protection service',
                'Contact ISP immediately',
                'Enable traffic filtering',
                'Implement geo-blocking if needed',
            ],
            'Man-in-the-Middle': [
                'Verify SSL certificates',
                'Update encryption protocols',
                'Check network integrity',
                'Audit VPN connections',
            ],
            'SQL Injection': [
                'Patch application immediately',
                'Review database access logs',
                'Implement parameterized queries',
                'Enable SQL query monitoring',
            ],
            'Cross-Site Scripting': [
                'Sanitize all user inputs',
                'Update security headers',
                'Patch vulnerabilities',
                'Run security audit',
            ],
            'Social Engineering': [
                'Train users on security',
                'Review access logs',
                'Implement additional verification',
                'Audit permission changes',
            ],
            'Zero-Day Exploit': [
                'Isolate system immediately',
                'Contact vendor for patches',
                'Monitor for further activity',
                'Document incident thoroughly',
            ],
            'Insider Threat': [
                'Review access logs',
                'Audit user permissions',
                'Investigate activity',
                'Implement additional monitoring',
            ],
            'Spoofing / Password Attack': [
                'Force password reset for all users',
                'Enable multi-factor authentication',
                'Review authentication logs',
                'Check for compromised credentials',
            ],
        }
        return recommendations.get(attack_type, ['Review security policies', 'Monitor device activity'])


def detect_attack(params: Dict) -> Tuple[str, float, str, int, List[str]]:
    """Wrapper function for attack detection."""
    return AttackDetector.detect_attack(params)

def get_attack_recommendations(attack_type: str) -> List[str]:
    """Wrapper function for getting recommendations."""
    return AttackDetector.get_recommendations(attack_type)
