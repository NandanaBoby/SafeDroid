# app_data.py
"""
Enhanced permission database with comprehensive risk analysis
Includes permission metadata, categories, risk levels, and historical tracking
"""

# Permission metadata with risk classification and descriptions
PERMISSION_METADATA = {
    # System Permissions
    "INTERNET": {
        "category": "SYSTEM",
        "risk_level": "NORMAL",
        "severity": 1,
        "description": "Allows app to access the internet",
        "privacy_impact": "LOW",
        "can_access": ["Network data", "Online services"],
        "dangerous": False
    },
    
    # Camera & Media Permissions
    "CAMERA": {
        "category": "HARDWARE",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Access to device camera",
        "privacy_impact": "CRITICAL",
        "can_access": ["Video recordings", "Photos", "Visual data"],
        "dangerous": True
    },
    "MICROPHONE": {
        "category": "HARDWARE",
        "risk_level": "DANGEROUS",
        "severity": 9,
        "description": "Access to device microphone",
        "privacy_impact": "CRITICAL",
        "can_access": ["Audio recordings", "Voice data", "Conversations"],
        "dangerous": True
    },
    "READ_EXTERNAL_STORAGE": {
        "category": "STORAGE",
        "risk_level": "DANGEROUS",
        "severity": 7,
        "description": "Read access to device storage",
        "privacy_impact": "CRITICAL",
        "can_access": ["Photos", "Videos", "Documents", "Personal files"],
        "dangerous": True
    },
    "WRITE_EXTERNAL_STORAGE": {
        "category": "STORAGE",
        "risk_level": "DANGEROUS",
        "severity": 7,
        "description": "Write access to device storage",
        "privacy_impact": "HIGH",
        "can_access": ["Modify files", "Create backups"],
        "dangerous": True
    },
    
    # Location Permissions
    "LOCATION": {
        "category": "LOCATION",
        "risk_level": "DANGEROUS",
        "severity": 9,
        "description": "Precise location tracking",
        "privacy_impact": "CRITICAL",
        "can_access": ["GPS coordinates", "Real-time location", "Location history"],
        "dangerous": True
    },
    "ACCESS_FINE_LOCATION": {
        "category": "LOCATION",
        "risk_level": "DANGEROUS",
        "severity": 9,
        "description": "Precise GPS location access",
        "privacy_impact": "CRITICAL",
        "can_access": ["GPS data", "Exact coordinates"],
        "dangerous": True
    },
    "ACCESS_COARSE_LOCATION": {
        "category": "LOCATION",
        "risk_level": "DANGEROUS",
        "severity": 6,
        "description": "Approximate location access (network-based)",
        "privacy_impact": "HIGH",
        "can_access": ["Approximate location", "Network-based location"],
        "dangerous": True
    },
    
    # Contact Permissions
    "CONTACTS": {
        "category": "PERSONAL_DATA",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Access to device contacts",
        "privacy_impact": "CRITICAL",
        "can_access": ["Contact list", "Phone numbers", "Email addresses", "Contact details"],
        "dangerous": True
    },
    "READ_CONTACTS": {
        "category": "PERSONAL_DATA",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Read contact information",
        "privacy_impact": "CRITICAL",
        "can_access": ["Contact data"],
        "dangerous": True
    },
    "WRITE_CONTACTS": {
        "category": "PERSONAL_DATA",
        "risk_level": "DANGEROUS",
        "severity": 7,
        "description": "Modify contact information",
        "privacy_impact": "HIGH",
        "can_access": ["Add/modify contacts"],
        "dangerous": True
    },
    
    # Communication Permissions
    "SMS": {
        "category": "COMMUNICATION",
        "risk_level": "DANGEROUS",
        "severity": 9,
        "description": "Send and receive SMS messages",
        "privacy_impact": "CRITICAL",
        "can_access": ["SMS content", "Message history"],
        "dangerous": True
    },
    "READ_SMS": {
        "category": "COMMUNICATION",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Read SMS messages",
        "privacy_impact": "CRITICAL",
        "can_access": ["SMS data"],
        "dangerous": True
    },
    "SEND_SMS": {
        "category": "COMMUNICATION",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Send SMS messages",
        "privacy_impact": "HIGH",
        "can_access": ["Send messages"],
        "dangerous": True
    },
    "CALL_LOG": {
        "category": "COMMUNICATION",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Access call history",
        "privacy_impact": "CRITICAL",
        "can_access": ["Call history", "Call duration", "Phone numbers called"],
        "dangerous": True
    },
    "READ_CALL_LOG": {
        "category": "COMMUNICATION",
        "risk_level": "DANGEROUS",
        "severity": 8,
        "description": "Read call logs",
        "privacy_impact": "CRITICAL",
        "can_access": ["Call records"],
        "dangerous": True
    },
    "WRITE_CALL_LOG": {
        "category": "COMMUNICATION",
        "risk_level": "DANGEROUS",
        "severity": 7,
        "description": "Modify call logs",
        "privacy_impact": "HIGH",
        "can_access": ["Modify call records"],
        "dangerous": True
    },
    
    # Phone Permissions
    "PHONE_STATE": {
        "category": "PHONE_INFO",
        "risk_level": "DANGEROUS",
        "severity": 6,
        "description": "Access phone state and identity",
        "privacy_impact": "HIGH",
        "can_access": ["Phone number", "IMEI", "Device ID"],
        "dangerous": True
    },
    "CALL_PHONE": {
        "category": "PHONE_INFO",
        "risk_level": "DANGEROUS",
        "severity": 7,
        "description": "Make phone calls",
        "privacy_impact": "HIGH",
        "can_access": ["Initiate calls"],
        "dangerous": True
    },
    
    # Calendar Permissions
    "READ_CALENDAR": {
        "category": "PERSONAL_DATA",
        "risk_level": "DANGEROUS",
        "severity": 7,
        "description": "Read calendar events",
        "privacy_impact": "HIGH",
        "can_access": ["Calendar events", "Meeting details", "Schedule"],
        "dangerous": True
    },
    "WRITE_CALENDAR": {
        "category": "PERSONAL_DATA",
        "risk_level": "DANGEROUS",
        "severity": 6,
        "description": "Create/modify calendar events",
        "privacy_impact": "MEDIUM",
        "can_access": ["Add/modify events"],
        "dangerous": True
    },
    
    # Account Permissions
    "GET_ACCOUNTS": {
        "category": "ACCOUNT",
        "risk_level": "DANGEROUS",
        "severity": 6,
        "description": "Access device accounts",
        "privacy_impact": "HIGH",
        "can_access": ["Account information", "Emails", "Usernames"],
        "dangerous": True
    },
    
    # Sensor Permissions
    "SENSORS": {
        "category": "HARDWARE",
        "risk_level": "DANGEROUS",
        "severity": 6,
        "description": "Access motion and sensor data",
        "privacy_impact": "MEDIUM",
        "can_access": ["Accelerometer", "Gyroscope", "Step counter"],
        "dangerous": True
    },
    
    # Device Admin (Most Dangerous)
    "DEVICE_ADMIN": {
        "category": "SYSTEM",
        "risk_level": "CRITICAL",
        "severity": 10,
        "description": "Device administration capabilities",
        "privacy_impact": "CRITICAL",
        "can_access": ["Full device control", "Password reset", "Device lock"],
        "dangerous": True
    }
}

# Permission categories
PERMISSION_CATEGORIES = {
    "SYSTEM": {
        "name": "System Permissions",
        "description": "Core system-level access"
    },
    "HARDWARE": {
        "name": "Hardware Access",
        "description": "Physical device sensors and hardware"
    },
    "STORAGE": {
        "name": "Storage Access",
        "description": "File system and storage access"
    },
    "LOCATION": {
        "name": "Location Tracking",
        "description": "GPS and location services"
    },
    "PERSONAL_DATA": {
        "name": "Personal Data",
        "description": "Private user information"
    },
    "COMMUNICATION": {
        "name": "Communication",
        "description": "Calls, messages, and communications"
    },
    "PHONE_INFO": {
        "name": "Phone Information",
        "description": "Device phone information"
    },
    "ACCOUNT": {
        "name": "Account Information",
        "description": "User account data"
    }
}

# Comprehensive app permission data with metadata
APP_PERMISSION_DATA = {
    "Instagram": [
        "INTERNET",
        "CAMERA",
        "MICROPHONE",
        "LOCATION"
    ],
    "WhatsApp": [
        "INTERNET",
        "CAMERA",
        "MICROPHONE",
        "CONTACTS"
    ],
    "FakeApp": [
        "INTERNET",
        "CAMERA",
        "MICROPHONE",
        "CONTACTS",
        "SMS",
        "CALL_LOG"
    ],
    "TikTok": [
        "INTERNET",
        "CAMERA",
        "MICROPHONE",
        "LOCATION",
        "READ_EXTERNAL_STORAGE"
    ],
    "Gmail": [
        "INTERNET",
        "GET_ACCOUNTS",
        "READ_CONTACTS"
    ]
}

# Permission correlations - dangerous combinations
PERMISSION_CORRELATIONS = {
    "SMS": ["CALL_LOG", "CONTACTS"],
    "CALL_LOG": ["SMS", "MICROPHONE"],
    "CAMERA": ["CONTACTS", "LOCATION"],
    "MICROPHONE": ["CALL_LOG", "CONTACTS"],
    "CONTACTS": ["SMS", "CALL_LOG", "LOCATION"],
    "LOCATION": ["CAMERA", "MICROPHONE"],
    "DEVICE_ADMIN": ["SMS", "CALL_LOG", "CONTACTS"],
    "GET_ACCOUNTS": ["CONTACTS", "READ_CALENDAR"]
}

# Risk thresholds for scoring
RISK_THRESHOLDS = {
    "LOW": (0, 15),
    "MEDIUM": (16, 45),
    "HIGH": (46, 85),
    "CRITICAL": (86, 100)
}

# Trusted publishers (whitelisted)
TRUSTED_PUBLISHERS = [
    "google",
    "apple",
    "microsoft",
    "meta",
    "whatsapp"
]
