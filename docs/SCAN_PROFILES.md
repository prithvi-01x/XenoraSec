# Scan Profiles & Engine Mode Specifications

XenoraSec provides preset and customizable scanning configurations tailored to different operational objectives.

## 1. Quick Recon (`quick`)
- **Objective**: Rapid surface mapping and initial triage.
- **Port Scope**: Top 100 ports (`--top-ports 100`).
- **Timing Policy**: T4 (Aggressive).
- **Nuclei Coverage**: Critical/High CVEs and basic technologies.
- **Estimated Runtime**: 1-2 minutes.

## 2. Full Web Audit (`full`)
- **Objective**: In-depth vulnerability audit for web applications and APIs.
- **Port Scope**: Standard ports (80, 443, 8080, 8443) + discovery.
- **Nuclei Coverage**: Full template categories (cves, misconfigurations, exposures, rce, xss, sqli).
- **Estimated Runtime**: 5-10 minutes.

## 3. Network Discovery (`network`)
- **Objective**: Infrastructure scanning, OS fingerprinting, and standard services.
- **Port Scope**: Ports 1-1024 + extended ports.
- **Engine Flags**: `-sV -O --version-intensity 5`.
- **Estimated Runtime**: 3-5 minutes.

## 4. Custom Mode (`custom`)
- **Objective**: Full operator control over parameters.
- **Customizations**: Arbitrary port specifications (e.g. `1-65535`, `80,443`), timing policies (T0-T5), OS detection toggles, and individual Nuclei template tag chips.
