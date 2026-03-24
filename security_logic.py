import re

def analyze_security(content: str) -> str:
    """
    Analyzes a given text or email message for security risks:
    - Spam indicators
    - Phishing links
    - Malware/Suspicious attachments or executable links
    - Privacy/PII exposure
    """
    report = []
    content_lower = content.lower()
    
    # 1. Spam Indicators
    spam_keywords = ["urgent", "winner", "lottery", "prize", "free money", "act now", "guaranteed", "exclusive offer"]
    spam_score = sum(1 for kw in spam_keywords if kw in content_lower)
    if spam_score >= 2:
        report.append("⚠️ SPAM ALERT: Message contains multiple high-pressure or manipulative keywords.")
        
    # 2. Phishing Detectors
    # Look for URLs that try to appear like real institutions or suspicious keywords
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    phishing_suspicion = False
    for url in urls:
        if any(suspicious in url.lower() for suspicious in ["login", "reset", "verify", "bank", "account", "secure"]):
            phishing_suspicion = True
            report.append(f"🛑 PHISHING ALERT: Suspicious credential-harvesting link found -> {url}")
            
    # 3. Malware / Suspicious Execution Links
    malware_extensions = [".exe", ".zip", ".scr", ".bat", ".cmd", ".msi", ".vbs"]
    for url in urls:
        if any(url.lower().endswith(ext) for ext in malware_extensions):
            report.append(f"☣️ MALWARE ALERT: Link points directly to a highly dangerous executable file: {url}")
            
    # 4. Privacy / PII Risks
    ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
    # Basic CC approximation requiring 13-16 digits often separated by spaces or dashes
    cc_pattern = r"\b(?:\d[ -]*?){13,16}\b"
    
    if re.search(ssn_pattern, content):
        report.append("👁️ PRIVACY LEAK: Possible Social Security Number detected in the text.")
    
    # Search for potential CC numbers, filtering out small harmless numbers
    potential_ccs = re.findall(cc_pattern, content)
    for pcc in potential_ccs:
        # Strip dashes and spaces to check raw length
        raw_num = pcc.replace(" ", "").replace("-", "")
        if 13 <= len(raw_num) <= 16:
            report.append("👁️ PRIVACY LEAK: Possible Credit Card number detected in the text.")
            break
            
    if not report:
        return "✅ SECURITY SCAN PASSED: No obvious spam, phishing, malware, or privacy risks detected in the text."
        
    return "🚨 AUTOMATED SECURITY REPORT 🚨\n\n" + "\n".join(report)

if __name__ == "__main__":
    # Test execution
    test_msg = "URGENT! Click here to reset your bank password http://fake-bank-login.com/secure.exe and provide your SSN 000-00-0000"
    print(analyze_security(test_msg))
