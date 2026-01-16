# risk_engine.py
"""
Advanced risk analysis engine for mobile app permission evaluation
Provides sophisticated permission analysis with correlation detection,
threat indicators, and comprehensive risk scoring
"""

from app_data import (
    PERMISSION_METADATA,
    PERMISSION_CATEGORIES,
    APP_PERMISSION_DATA,
    PERMISSION_CORRELATIONS,
    RISK_THRESHOLDS,
    TRUSTED_PUBLISHERS
)


class PermissionAnalyzer:
    """Advanced permission analyzer with complex risk evaluation"""
    
    def __init__(self):
        self.permission_metadata = PERMISSION_METADATA
        self.permission_categories = PERMISSION_CATEGORIES
        self.permission_correlations = PERMISSION_CORRELATIONS
        self.risk_thresholds = RISK_THRESHOLDS
    
    def calculate_severity_score(self, permissions: list) -> dict:
        """
        Calculate detailed severity score based on permission severity levels
        
        Args:
            permissions: List of permission strings
            
        Returns:
            Dict with total_score, category_scores, severity_breakdown
        """
        total_score = 0
        category_scores = {}
        severity_breakdown = {
            "critical": [],
            "dangerous": [],
            "normal": []
        }
        
        for perm in permissions:
            if perm in self.permission_metadata:
                meta = self.permission_metadata[perm]
                severity = meta.get("severity", 0)
                category = meta.get("category", "UNKNOWN")
                
                total_score += severity
                
                # Track category scores
                if category not in category_scores:
                    category_scores[category] = 0
                category_scores[category] += severity
                
                # Breakdown by severity
                if severity >= 8:
                    severity_breakdown["critical"].append({
                        "permission": perm,
                        "severity": severity,
                        "description": meta.get("description", "")
                    })
                elif severity >= 5:
                    severity_breakdown["dangerous"].append({
                        "permission": perm,
                        "severity": severity,
                        "description": meta.get("description", "")
                    })
                else:
                    severity_breakdown["normal"].append({
                        "permission": perm,
                        "severity": severity,
                        "description": meta.get("description", "")
                    })
        
        return {
            "total_score": total_score,
            "category_scores": category_scores,
            "severity_breakdown": severity_breakdown,
            "critical_count": len(severity_breakdown["critical"]),
            "dangerous_count": len(severity_breakdown["dangerous"]),
            "normal_count": len(severity_breakdown["normal"])
        }
    
    def detect_permission_correlations(self, permissions: list) -> dict:
        """
        Detect suspicious permission correlations and patterns
        
        Args:
            permissions: List of permission strings
            
        Returns:
            Dict with detected correlations and risk patterns
        """
        correlations = []
        suspicious_patterns = []
        
        for perm in permissions:
            if perm in self.permission_correlations:
                related_perms = self.permission_correlations[perm]
                found_related = [p for p in related_perms if p in permissions]
                
                if found_related:
                    correlations.append({
                        "primary": perm,
                        "correlated": found_related,
                        "count": len(found_related)
                    })
        
        # Detect suspicious patterns
        if "SMS" in permissions and "CALL_PHONE" in permissions:
            suspicious_patterns.append("App can intercept SMS and make calls - VERY SUSPICIOUS")
        
        if "DEVICE_ADMIN" in permissions:
            suspicious_patterns.append("Device admin access requested - CRITICAL THREAT")
        
        if ("READ_CONTACTS" in permissions and 
            "READ_SMS" in permissions and 
            "CALL_LOG" in permissions):
            suspicious_patterns.append("Full communication profile access - EXTREME DATA COLLECTION")
        
        if ("CAMERA" in permissions and 
            "MICROPHONE" in permissions and 
            "ACCESS_FINE_LOCATION" in permissions):
            suspicious_patterns.append("Complete surveillance capability detected")
        
        return {
            "correlations": correlations,
            "suspicious_patterns": suspicious_patterns,
            "pattern_risk_level": "CRITICAL" if suspicious_patterns else "NORMAL"
        }
    
    def analyze_privacy_impact(self, permissions: list) -> dict:
        """
        Analyze privacy impact categorized by data type
        
        Args:
            permissions: List of permission strings
            
        Returns:
            Dict with privacy impact analysis
        """
        privacy_impacts = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        affected_data_types = set()
        
        for perm in permissions:
            if perm in self.permission_metadata:
                meta = self.permission_metadata[perm]
                impact = meta.get("privacy_impact", "LOW")
                
                privacy_impacts[impact].append({
                    "permission": perm,
                    "description": meta.get("description", ""),
                    "can_access": meta.get("can_access", [])
                })
                
                affected_data_types.update(meta.get("can_access", []))
        
        return {
            "privacy_impacts": privacy_impacts,
            "affected_data_types": list(affected_data_types),
            "critical_data_access": len(privacy_impacts["CRITICAL"]) > 0,
            "data_types_count": len(affected_data_types)
        }
    
    def categorize_permissions(self, permissions: list) -> dict:
        """
        Categorize permissions by functional groups
        
        Args:
            permissions: List of permission strings
            
        Returns:
            Dict with categorized permissions
        """
        categorized = {}
        
        for perm in permissions:
            if perm in self.permission_metadata:
                category = self.permission_metadata[perm]["category"]
                
                if category not in categorized:
                    categorized[category] = {
                        "name": self.permission_categories[category]["name"],
                        "permissions": []
                    }
                
                categorized[category]["permissions"].append({
                    "name": perm,
                    "severity": self.permission_metadata[perm]["severity"],
                    "risk_level": self.permission_metadata[perm]["risk_level"]
                })
        
        return categorized
    
    def calculate_risk_level(self, score: int) -> str:
        """
        Map score to risk level based on thresholds
        
        Args:
            score: Total risk score
            
        Returns:
            Risk level string (LOW, MEDIUM, HIGH, CRITICAL)
        """
        for level, threshold in self.risk_thresholds.items():
            # Handle both dict and tuple formats
            if isinstance(threshold, dict):
                if threshold.get("min", 0) <= score <= threshold.get("max", 100):
                    return level
            elif isinstance(threshold, tuple):
                if threshold[0] <= score <= threshold[1]:
                    return level
        return "CRITICAL"
    
    def detect_threat_indicators(self, app_name: str) -> dict:
        """
        Detect specific threat indicators for an app
        
        Args:
            app_name: Name of the application
            
        Returns:
            Dict with detected threat indicators
        """
        indicators = {
            "privilege_escalation": False,
            "data_exfiltration_risk": "LOW",
            "financial_risk": "LOW",
            "privacy_risk": "LOW",
            "detected_threats": []
        }
        
        if app_name not in APP_PERMISSION_DATA:
            return indicators
        
        app_data = APP_PERMISSION_DATA[app_name]
        
        # Handle both list and dict formats
        if isinstance(app_data, list):
            permissions = app_data
            dangerous_permissions = [p for p in permissions if p in PERMISSION_METADATA and PERMISSION_METADATA[p].get("dangerous", False)]
        else:
            permissions = app_data.get("declared_permissions", [])
            dangerous_permissions = app_data.get("dangerous_permissions", [])
        
        # Check for privilege escalation
        if "DEVICE_ADMIN" in permissions:
            indicators["privilege_escalation"] = True
            indicators["detected_threats"].append("Device admin access")
        
        # Assess data exfiltration risk
        dangerous_count = len(dangerous_permissions)
        if dangerous_count > 10:
            indicators["data_exfiltration_risk"] = "CRITICAL"
            indicators["detected_threats"].append("Excessive dangerous permissions")
        elif dangerous_count > 6:
            indicators["data_exfiltration_risk"] = "HIGH"
        elif dangerous_count > 3:
            indicators["data_exfiltration_risk"] = "MEDIUM"
        
        # Financial risk assessment
        if "SEND_SMS" in permissions or "CALL_PHONE" in permissions:
            indicators["financial_risk"] = "HIGH"
            indicators["detected_threats"].append("Can make calls or send SMS (financial risk)")
        
        # Privacy risk
        if len(permissions) > 15:
            indicators["privacy_risk"] = "CRITICAL"
            indicators["detected_threats"].append("Unusually high number of permission requests")
        elif len(permissions) > 10:
            indicators["privacy_risk"] = "HIGH"
        
        return indicators
    
    def analyze_app_comprehensive(self, app_name: str) -> dict:
        """
        Comprehensive app analysis using all available data
        
        Args:
            app_name: Name of the application to analyze
            
        Returns:
            Complete risk analysis report
        """
        if app_name not in APP_PERMISSION_DATA:
            return {"error": "App not found in database"}
        
        app_data = APP_PERMISSION_DATA[app_name]
        
        # Handle both list format and dict format
        if isinstance(app_data, list):
            permissions = app_data
            version = "Unknown"
            dangerous_permissions = [p for p in permissions if p in PERMISSION_METADATA and PERMISSION_METADATA[p].get("dangerous", False)]
            runtime_permissions = []
            risk_profile = {}
            permission_justification = {}
            historical_changes = []
        else:
            permissions = app_data.get("declared_permissions", [])
            version = app_data.get("version", "Unknown")
            dangerous_permissions = app_data.get("dangerous_permissions", [])
            runtime_permissions = app_data.get("runtime_permissions", [])
            risk_profile = app_data.get("risk_profile", {})
            permission_justification = app_data.get("permission_justification", {})
            historical_changes = app_data.get("historical_changes", [])
        
        # Run all analyses
        severity_analysis = self.calculate_severity_score(permissions)
        correlation_analysis = self.detect_permission_correlations(permissions)
        privacy_analysis = self.analyze_privacy_impact(permissions)
        categorized = self.categorize_permissions(permissions)
        threat_indicators = self.detect_threat_indicators(app_name)
        
        total_score = severity_analysis["total_score"]
        risk_level = self.calculate_risk_level(total_score)
        
        return {
            "app_name": app_name,
            "version": version,
            "risk_score": total_score,
            "risk_level": risk_level,
            
            # Permission analysis
            "permission_analysis": {
                "total_declared": len(permissions),
                "dangerous_count": len(dangerous_permissions),
                "runtime_requested": len(runtime_permissions),
                "severity_breakdown": severity_analysis["severity_breakdown"],
                "category_scores": severity_analysis["category_scores"]
            },
            
            # Risk assessment
            "risk_assessment": {
                "severity": severity_analysis,
                "correlations": correlation_analysis,
                "threat_indicators": threat_indicators
            },
            
            # Privacy impact
            "privacy_analysis": privacy_analysis,
            
            # Categorization
            "categorized_permissions": categorized,
            
            # Risk profile from app data
            "risk_profile": risk_profile,
            
            # Permission justifications
            "permission_justification": permission_justification,
            
            # Historical changes
            "version_history": historical_changes,
            
            # Threat indicators
            "threat_indicators": threat_indicators
        }


# Backwards compatibility functions
def calculate_risk(permissions: list) -> tuple:
    """
    Legacy function for backward compatibility
    Returns simple risk score, level, and explanations
    """
    analyzer = PermissionAnalyzer()
    severity_data = analyzer.calculate_severity_score(permissions)
    correlations = analyzer.detect_permission_correlations(permissions)
    
    score = severity_data["total_score"]
    level = analyzer.calculate_risk_level(score)
    
    explanations = []
    
    # Add severity explanations
    for perm_info in severity_data["severity_breakdown"]["critical"]:
        explanations.append(
            f"[CRITICAL] {perm_info['permission']}: {perm_info['description']} (Severity: {perm_info['severity']})"
        )
    
    for perm_info in severity_data["severity_breakdown"]["dangerous"]:
        explanations.append(
            f"[DANGEROUS] {perm_info['permission']}: {perm_info['description']}"
        )
    
    # Add pattern warnings
    for pattern in correlations["suspicious_patterns"]:
        explanations.append(f"[PATTERN] {pattern}")
    
    return score, level, explanations


def analyze_app(app_name: str) -> dict:
    """
    Main entry point for comprehensive app analysis
    """
    analyzer = PermissionAnalyzer()
    return analyzer.analyze_app_comprehensive(app_name)

