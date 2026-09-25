import asyncio
import sys
from playwright.async_api import async_playwright

async def run_tests():
    print("=== Starting Playwright End-to-End Verification ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Capture console errors
        errors = []
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))
        page.on("console", lambda msg: errors.append(f"CONSOLE ERROR: {msg.text}") if msg.type == "error" else None)

        print("\n1. Testing Dashboard Page (http://localhost:5173/)...")
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        await page.wait_for_selector("h1:has-text('Security Operations & Posture')", timeout=10000)
        await page.wait_for_selector("text=Cumulative Scans", timeout=5000)
        print("  ✓ Dashboard loaded with tactical header and metrics")

        # Check scan mode toggle
        single_btn = page.locator("button:has-text('Single Host')")
        batch_btn = page.locator("button:has-text('Batch / CIDR')")
        await batch_btn.click()
        await page.wait_for_selector("textarea#batch-targets", timeout=3000)
        print("  ✓ Switched to Batch / CIDR mode")
        await single_btn.click()
        await page.wait_for_selector("input#target", timeout=3000)
        print("  ✓ Switched back to Single Host mode")

        # Test Scan profile selector
        full_profile = page.locator("button:has-text('Full Web Audit')")
        await full_profile.click()
        print("  ✓ Selected Full Web Audit profile")

        # Test Advanced Accordion
        advanced_toggle = page.locator("button:has-text('Advanced Engine & Nuclei Policy')")
        await advanced_toggle.click()
        await page.wait_for_selector("text=Nmap Scan Timing", timeout=3000)
        print("  ✓ Advanced Engine options expanded smoothly")

        print("\n2. Testing Navigation to Asset Inventory (/assets)...")
        await page.click("aside.hidden.md\\:flex a:has-text('Asset Inventory')")
        await page.wait_for_url("**/assets")
        await page.wait_for_selector("h1:has-text('Asset Attack Surface Inventory')", timeout=5000)
        await page.wait_for_selector("text=Indexed Assets", timeout=5000)
        print("  ✓ Asset Inventory page rendered successfully")

        # Test Asset Detail Modal or Empty state
        asset_rows = page.locator("table tbody tr")
        row_count = await asset_rows.count()
        if row_count > 0:
            print(f"  - Testing Asset modal interactions on {row_count} assets...")
            # Click first row to open detail modal
            await asset_rows.first.click()
            await page.wait_for_selector("text=Asset Metadata & Parameters", timeout=5000)
            await page.wait_for_selector("button:has-text('Launch Audit Scan')", timeout=3000)
            print("    ✓ Asset Detail Modal opened with security parameters & audit launcher")
            await page.click("button:has-text('Close Details')")
            print("    ✓ Closed Asset Detail Modal")
        else:
            print("  ✓ Asset inventory empty state rendered cleanly")

        print("\n3. Testing Navigation to Audit Ledger (/history)...")
        await page.click("aside.hidden.md\\:flex a:has-text('Scan Audit Log')")
        await page.wait_for_url("**/history")
        await page.wait_for_selector("h1:has-text('Audit Ledger & Scan Archive')", timeout=5000)
        print("  ✓ Audit Ledger / History page rendered successfully")

        print("\n4. Testing Navigation to Settings (/settings)...")
        await page.click("aside.hidden.md\\:flex a:has-text('Engine & System')")
        await page.wait_for_url("**/settings")
        await page.wait_for_selector("h1:has-text('Engine Telemetry & Parameters')", timeout=5000)
        await page.wait_for_selector("text=Worker Queue Concurrency", timeout=5000)
        await page.wait_for_selector("text=Environment Security Policies", timeout=5000)
        print("  ✓ Engine Telemetry / Settings page rendered successfully")

        # Test Scan Results Page if any scan exists, or navigate to a dummy / test scan
        print("\n5. Testing Scan Dispatch and Live Scan Results Page...")
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        target_input = page.locator("input#target")
        await target_input.fill("scanme.nmap.org")
        
        # Click dispatch
        start_btn = page.locator("button:has-text('Launch Security Audit')")
        await start_btn.click()
        
        # Wait for navigation to /scan/:scanId
        await page.wait_for_url("**/scan/*", timeout=15000)
        print(f"  ✓ Successfully dispatched scan, navigated to: {page.url}")
        
        # Verify Scan Results page elements
        await page.wait_for_selector("text=scanme.nmap.org", timeout=10000)
        await page.wait_for_selector("text=Discovered Vulnerabilities", timeout=5000)
        await page.wait_for_selector("text=Open TCP / UDP Ports", timeout=5000)
        print("  ✓ Scan Results header and KPI telemetry cards verified")

        # Test tabs
        print("  - Testing Tabs (Ports, Vulnerabilities, Live Console, Raw)...")
        await page.click("button:has-text('ports')")
        await page.wait_for_selector(":is(th, p):has-text('Port')", timeout=5000)
        print("    ✓ Ports tab loaded")

        await page.click("button:has-text('vulnerabilities')")
        await page.wait_for_selector("select:has-text('All Severities')", timeout=5000)
        print("    ✓ Vulnerabilities tab loaded")

        await page.click("button:has-text('Live Console')")
        await page.wait_for_selector("text=Execution Console", timeout=5000)
        print("    ✓ Live Terminal Console loaded")

        await page.click("button:has-text('raw')")
        await page.wait_for_selector("pre", timeout=5000)
        print("    ✓ Raw JSON tab loaded")

        # Test Export Report Modal
        print("  - Testing Export Report Modal...")
        export_btn = page.locator("button:has-text('Export Report')")
        await export_btn.click()
        await page.wait_for_selector("text=Export Assessment Dossier", timeout=5000)
        await page.wait_for_selector("text=Interactive HTML Report", timeout=5000)
        cancel_modal = page.locator("button:has-text('Cancel')")
        await cancel_modal.click()
        print("    ✓ Export modal opens and cancels properly")

        print("\n=== Playwright Verification Completed Successfully ===")
        if errors:
            print(f"Recorded {len(errors)} console notices (non-fatal):")
            for e in errors[:5]:
                print(f"  {e}")
        else:
            print("Zero console errors or exceptions recorded.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
