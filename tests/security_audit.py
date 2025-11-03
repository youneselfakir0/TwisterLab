"""
TwisterLab v1.0.0 - Security Audit Script
Runs comprehensive security scans: Bandit, Safety, Trivy
Generates security_audit_report.md with findings and recommendations.
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class SecurityAuditor:
    """Security audit framework for TwisterLab"""
    
    def __init__(self):
        self.findings: Dict[str, Any] = {
            "bandit": {},
            "safety": {},
            "trivy": {}
        }
        self.report_path = Path("security_audit_report.md")
    
    def run_bandit(self) -> Dict[str, Any]:
        """
        Run Bandit Python security scanner.
        
        Returns:
            Bandit results dict
        """
        print("\n🔍 Running Bandit (Python code security analysis)...")
        
        try:
            result = subprocess.run(
                ["bandit", "-r", "agents/", "-f", "json", "-o", "bandit_report.json"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if Path("bandit_report.json").exists():
                with open("bandit_report.json", "r") as f:
                    bandit_data = json.load(f)
                
                # Extract summary
                metrics = bandit_data.get("metrics", {})
                total_issues = len(bandit_data.get("results", []))
                
                # Count by severity
                severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                for issue in bandit_data.get("results", []):
                    severity = issue.get("issue_severity", "LOW")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                print(f"  ✅ Bandit scan complete")
                print(f"  Total issues: {total_issues}")
                print(f"  HIGH: {severity_counts['HIGH']}, MEDIUM: {severity_counts['MEDIUM']}, LOW: {severity_counts['LOW']}")
                
                return {
                    "status": "completed",
                    "total_issues": total_issues,
                    "severity_counts": severity_counts,
                    "results": bandit_data.get("results", [])[:10],  # Top 10 issues
                    "metrics": metrics
                }
            else:
                print("  ⚠️  Bandit report not generated")
                return {"status": "no_report", "error": "Report file not found"}
        
        except FileNotFoundError:
            print("  ❌ Bandit not installed")
            print("  Install: pip install bandit")
            return {"status": "not_installed", "tool": "bandit"}
        
        except subprocess.TimeoutExpired:
            print("  ❌ Bandit scan timeout (5 min)")
            return {"status": "timeout"}
        
        except Exception as e:
            print(f"  ❌ Bandit scan failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_safety(self) -> Dict[str, Any]:
        """
        Run Safety dependency vulnerability scanner.
        
        Returns:
            Safety results dict
        """
        print("\n🔍 Running Safety (dependency vulnerability scan)...")
        
        try:
            result = subprocess.run(
                ["safety", "check", "--json", "--output", "safety_report.json"],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if Path("safety_report.json").exists():
                with open("safety_report.json", "r") as f:
                    safety_data = json.load(f)
                
                vulnerabilities = safety_data if isinstance(safety_data, list) else []
                total_vulns = len(vulnerabilities)
                
                # Extract package names
                vulnerable_packages = set()
                for vuln in vulnerabilities:
                    if isinstance(vuln, dict):
                        pkg = vuln.get("package", "unknown")
                        vulnerable_packages.add(pkg)
                
                print(f"  ✅ Safety scan complete")
                print(f"  Vulnerabilities found: {total_vulns}")
                print(f"  Vulnerable packages: {len(vulnerable_packages)}")
                
                return {
                    "status": "completed",
                    "total_vulnerabilities": total_vulns,
                    "vulnerable_packages": list(vulnerable_packages),
                    "vulnerabilities": vulnerabilities[:10]  # Top 10
                }
            else:
                print("  ⚠️  Safety report not generated")
                return {"status": "no_report"}
        
        except FileNotFoundError:
            print("  ❌ Safety not installed")
            print("  Install: pip install safety")
            return {"status": "not_installed", "tool": "safety"}
        
        except subprocess.TimeoutExpired:
            print("  ❌ Safety scan timeout (3 min)")
            return {"status": "timeout"}
        
        except Exception as e:
            print(f"  ❌ Safety scan failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_trivy(self) -> Dict[str, Any]:
        """
        Run Trivy Docker image scanner.
        
        Returns:
            Trivy results dict
        """
        print("\n🔍 Running Trivy (Docker image security scan)...")
        
        try:
            # Check if Docker image exists
            check_image = subprocess.run(
                ["docker", "images", "twisterlab-api:staging", "-q"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not check_image.stdout.strip():
                print("  ⚠️  Docker image 'twisterlab-api:staging' not found")
                print("  Build image: docker build -t twisterlab-api:staging .")
                return {"status": "image_not_found"}
            
            # Run Trivy scan
            result = subprocess.run(
                [
                    "trivy", "image",
                    "--format", "json",
                    "--output", "trivy_report.json",
                    "twisterlab-api:staging"
                ],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if Path("trivy_report.json").exists():
                with open("trivy_report.json", "r") as f:
                    trivy_data = json.load(f)
                
                # Extract vulnerabilities
                total_vulns = 0
                severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
                
                for target in trivy_data.get("Results", []):
                    for vuln in target.get("Vulnerabilities", []):
                        total_vulns += 1
                        severity = vuln.get("Severity", "UNKNOWN")
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                print(f"  ✅ Trivy scan complete")
                print(f"  Total vulnerabilities: {total_vulns}")
                print(f"  CRITICAL: {severity_counts['CRITICAL']}, HIGH: {severity_counts['HIGH']}")
                
                return {
                    "status": "completed",
                    "total_vulnerabilities": total_vulns,
                    "severity_counts": severity_counts,
                    "results": trivy_data.get("Results", [])
                }
            else:
                print("  ⚠️  Trivy report not generated")
                return {"status": "no_report"}
        
        except FileNotFoundError:
            print("  ❌ Trivy not installed")
            print("  Install: https://aquasecurity.github.io/trivy/latest/getting-started/installation/")
            return {"status": "not_installed", "tool": "trivy"}
        
        except subprocess.TimeoutExpired:
            print("  ❌ Trivy scan timeout (5 min)")
            return {"status": "timeout"}
        
        except Exception as e:
            print(f"  ❌ Trivy scan failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_report(self):
        """Generate comprehensive security audit report in Markdown"""
        print("\n📝 Generating security audit report...")
        
        report = []
        report.append("# 🔒 TwisterLab v1.0.0 - Security Audit Report")
        report.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Version:** v1.0.0")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("## Executive Summary\n")
        
        total_issues = 0
        critical_high = 0
        
        # Bandit summary
        if self.findings["bandit"].get("status") == "completed":
            bandit_issues = self.findings["bandit"]["total_issues"]
            total_issues += bandit_issues
            critical_high += self.findings["bandit"]["severity_counts"].get("HIGH", 0)
            report.append(f"- **Bandit (Python Code):** {bandit_issues} issues found")
        
        # Safety summary
        if self.findings["safety"].get("status") == "completed":
            safety_vulns = self.findings["safety"]["total_vulnerabilities"]
            total_issues += safety_vulns
            report.append(f"- **Safety (Dependencies):** {safety_vulns} vulnerabilities found")
        
        # Trivy summary
        if self.findings["trivy"].get("status") == "completed":
            trivy_vulns = self.findings["trivy"]["total_vulnerabilities"]
            total_issues += trivy_vulns
            critical_high += self.findings["trivy"]["severity_counts"].get("CRITICAL", 0)
            critical_high += self.findings["trivy"]["severity_counts"].get("HIGH", 0)
            report.append(f"- **Trivy (Docker Image):** {trivy_vulns} vulnerabilities found")
        
        report.append(f"\n**Total Issues:** {total_issues}")
        report.append(f"**Critical/High Severity:** {critical_high}\n")
        
        # Risk Assessment
        report.append("## Risk Assessment\n")
        if critical_high == 0:
            report.append("✅ **LOW RISK** - No critical or high-severity vulnerabilities found.\n")
        elif critical_high <= 5:
            report.append("⚠️  **MEDIUM RISK** - Some critical/high-severity issues require attention.\n")
        else:
            report.append("❌ **HIGH RISK** - Multiple critical/high-severity vulnerabilities detected.\n")
        
        # Bandit Details
        report.append("---\n")
        report.append("## 1. Bandit - Python Code Security Analysis\n")
        
        if self.findings["bandit"].get("status") == "completed":
            bandit = self.findings["bandit"]
            report.append(f"**Status:** ✅ Completed")
            report.append(f"**Total Issues:** {bandit['total_issues']}")
            report.append(f"**Severity Breakdown:**")
            report.append(f"- HIGH: {bandit['severity_counts']['HIGH']}")
            report.append(f"- MEDIUM: {bandit['severity_counts']['MEDIUM']}")
            report.append(f"- LOW: {bandit['severity_counts']['LOW']}\n")
            
            if bandit["results"]:
                report.append("### Top Issues:\n")
                for i, issue in enumerate(bandit["results"][:5], 1):
                    report.append(f"{i}. **{issue['issue_text']}**")
                    report.append(f"   - File: `{issue['filename']}:{issue['line_number']}`")
                    report.append(f"   - Severity: {issue['issue_severity']}")
                    report.append(f"   - Confidence: {issue['issue_confidence']}\n")
        else:
            report.append(f"**Status:** ❌ {self.findings['bandit'].get('status', 'Not run')}\n")
        
        # Safety Details
        report.append("---\n")
        report.append("## 2. Safety - Dependency Vulnerability Scan\n")
        
        if self.findings["safety"].get("status") == "completed":
            safety = self.findings["safety"]
            report.append(f"**Status:** ✅ Completed")
            report.append(f"**Total Vulnerabilities:** {safety['total_vulnerabilities']}")
            report.append(f"**Vulnerable Packages:** {', '.join(safety['vulnerable_packages']) if safety['vulnerable_packages'] else 'None'}\n")
            
            if safety["vulnerabilities"]:
                report.append("### Critical Vulnerabilities:\n")
                for i, vuln in enumerate(safety["vulnerabilities"][:5], 1):
                    if isinstance(vuln, dict):
                        report.append(f"{i}. **{vuln.get('package', 'Unknown')}** {vuln.get('installed_version', '')}")
                        report.append(f"   - CVE: {vuln.get('cve', 'N/A')}")
                        report.append(f"   - Advisory: {vuln.get('advisory', 'N/A')}")
                        report.append(f"   - Fix: Upgrade to {vuln.get('fixed_in', 'latest')}\n")
        else:
            report.append(f"**Status:** ❌ {self.findings['safety'].get('status', 'Not run')}\n")
        
        # Trivy Details
        report.append("---\n")
        report.append("## 3. Trivy - Docker Image Security Scan\n")
        
        if self.findings["trivy"].get("status") == "completed":
            trivy = self.findings["trivy"]
            report.append(f"**Status:** ✅ Completed")
            report.append(f"**Total Vulnerabilities:** {trivy['total_vulnerabilities']}")
            report.append(f"**Severity Breakdown:**")
            report.append(f"- CRITICAL: {trivy['severity_counts']['CRITICAL']}")
            report.append(f"- HIGH: {trivy['severity_counts']['HIGH']}")
            report.append(f"- MEDIUM: {trivy['severity_counts']['MEDIUM']}")
            report.append(f"- LOW: {trivy['severity_counts']['LOW']}\n")
        else:
            report.append(f"**Status:** ❌ {self.findings['trivy'].get('status', 'Not run')}\n")
        
        # Recommendations
        report.append("---\n")
        report.append("## Recommendations\n")
        report.append("1. **Update Dependencies:** Run `pip install --upgrade -r requirements.txt`")
        report.append("2. **Review Bandit Findings:** Fix HIGH severity issues in Python code")
        report.append("3. **Patch Docker Image:** Update base image and rebuild containers")
        report.append("4. **Enable Automated Scanning:** Add security scans to CI/CD pipeline")
        report.append("5. **Regular Audits:** Schedule monthly security audits")
        report.append("\n---\n")
        
        report.append(f"\n**Report Generated:** {datetime.now().isoformat()}")
        report.append(f"\n**Tool Versions:**")
        report.append(f"- Bandit: Check with `bandit --version`")
        report.append(f"- Safety: Check with `safety --version`")
        report.append(f"- Trivy: Check with `trivy --version`\n")
        
        # Write report
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        print(f"  ✅ Report saved: {self.report_path}")
    
    def run_all_scans(self):
        """Execute all security scans"""
        print(f"\n{'='*60}")
        print("  TwisterLab v1.0.0 - Security Audit")
        print(f"{'='*60}")
        
        # Run scans
        self.findings["bandit"] = self.run_bandit()
        self.findings["safety"] = self.run_safety()
        self.findings["trivy"] = self.run_trivy()
        
        # Generate report
        self.generate_report()
        
        print(f"\n{'='*60}")
        print("  Security Audit Complete")
        print(f"{'='*60}\n")
        print(f"Review report: {self.report_path}")
        print(f"View detailed results:")
        print(f"  - bandit_report.json")
        print(f"  - safety_report.json")
        print(f"  - trivy_report.json\n")


if __name__ == "__main__":
    auditor = SecurityAuditor()
    auditor.run_all_scans()
