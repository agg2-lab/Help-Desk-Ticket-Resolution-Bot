from typing import Dict, List

# Focused troubleshooting references for common campus support requests.
TROUBLESHOOTING_PLAYBOOK: Dict[str, List[str]] = {
    "login": [
        "Confirm the user is using the correct NetID and not an email alias.",
        "Verify caps lock and keyboard layout are correct.",
        "Check if password was recently changed; if so, advise sign-out/in on all devices.",
        "If locked out, direct user to official account recovery/reset flow.",
        "Escalate if account shows disabled or repeated lockouts continue.",
    ],
    "duo_mfa": [
        "Check phone date/time sync and Duo app notifications enabled.",
        "Try alternate MFA method (passcode, call, backup device) if push fails.",
        "Confirm the enrolled device is still active in Duo settings.",
        "If device lost/replaced, route to identity verification and device re-enrollment.",
    ],
    "wifi": [
        "Use the official campus SSID and forget/rejoin the network.",
        "Re-enter credentials with username format expected by campus IT.",
        "Run OS updates and restart network adapter.",
        "If dorm/building specific outage is suspected, escalate to network operations.",
    ],
    "vpn_firewall": [
        "Validate VPN client version and user entitlement.",
        "Check if local firewall/antivirus is blocking VPN ports or app executable.",
        "Try alternate network (hotspot) to isolate ISP/router restrictions.",
        "Collect error code/log snippet before escalation.",
    ],
    "email": [
        "Verify mailbox quota and account service health.",
        "Check spam/junk and safe-sender rules.",
        "Re-authenticate account in Outlook/webmail after credential changes.",
        "Escalate for mail flow tracing when external sender issues persist.",
    ],
    "lms": [
        "Test in a private browser window to isolate cached session issues.",
        "Disable extensions and allow third-party cookies for auth redirects.",
        "Confirm course enrollment is active in SIS/LMS sync.",
        "Escalate with course ID and timestamp if only one class is affected.",
    ],
    "general": [
        "Gather exact error text, time of issue, and impacted system.",
        "Ask what changed recently (password reset, OS update, new device).",
        "Attempt restart and retest in a clean browser profile.",
        "Escalate with reproducible steps and screenshots/log details.",
    ],
}


KEYWORD_TO_CATEGORY = {
    "netid": "login",
    "password": "login",
    "sign in": "login",
    "login": "login",
    "duo": "duo_mfa",
    "mfa": "duo_mfa",
    "2fa": "duo_mfa",
    "wifi": "wifi",
    "wireless": "wifi",
    "eduroam": "wifi",
    "vpn": "vpn_firewall",
    "firewall": "vpn_firewall",
    "forticlient": "vpn_firewall",
    "email": "email",
    "outlook": "email",
    "d2l": "lms",
    "brightspace": "lms",
    "canvas": "lms",
    "lms": "lms",
}
