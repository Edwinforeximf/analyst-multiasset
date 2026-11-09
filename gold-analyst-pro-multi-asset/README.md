# Gold Analyst Pro — Live Feed + Screenshot V2

**Live indicative market feed / multi-asset research.** See [UPGRADE_LIVE_DARI_HP.md](UPGRADE_LIVE_DARI_HP.md) for Railway + GitHub upgrade details. Existing screenshot mode, user accounts, reviewer flow and DOCX are retained.

Provider: Twelve Data (API key required). Quote, timestamp, D1/H4/H1 OHLC, rule-based directional BUY/SELL bias with separate `execution_ready`. For screenshots, Gemini continues to provide technical analysis. No trades are placed. For production broker publications, use a licensed feed and verify with broker prices.

# Gold Analyst Pro — Multi-Asset Edition

A new, standalone project (not a patch of the previous app). Multi-user Gemini screenshot research for **XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, USOIL**. Responsive Android-friendly web dashboard plus a GitHub Actions native Android WebView build.

## Features

- Select symbol → upload D1, H4, H1 screenshots (M15 optional) → Gemini analysis.
- Five-part Indonesian research, BUY/SELL/WAIT, technical bias, audit notes, levels, R/R.
- Conservative numerical validation: bad/missing levels become WAIT; no invented live data.
- H1 price-axis annotations if Gemini extracts *consistent* screenshot axis anchors. Levels outside the chart or when calibration fails remain in a clearly labeled side panel. **Axes are estimated and must be checked by a reviewer**.
- Centered 10% transparent uploaded company watermark on annotated H1; premium high-contrast 1080x1440 infographic.
- Analyst, Senior Analyst, Admin; review and approve/revise/reject.
- Export full DOCX (article + chart + infographic), TXT, chart/infographic PNG, clipboard copy.
- Multi-asset precision: metals/oil 2–3 decimals; EURUSD/GBPUSD 5; USDJPY 3.

## Deploy from Android/Chrome to Railway

1. Create **a NEW private GitHub repository** (e.g. `multi-asset-analyst-pro`). **Do not replace your running `gold-analyst-pro` service.** Upload the contents of this archive, preserving directories, including `.github` and `android-app`.
2. Railway → New Project → Deploy from GitHub repo → choose **the new** repository. Dockerfile is at repository root; leave Root Directory `/` (unless the uploaded project is nested).
3. Attach a **Railway Volume mounted at `/data`**, so accounts and screenshots survive redeploy. Keep a single worker/replica (SQLite + Volume are not suitable for multi-replica scale).
4. Railway → service → Variables (enter secrets **only here**, not in GitHub):
   - `GEMINI_API_KEY` = your Google AI Studio key
   - `GEMINI_MODEL` = `gemini-3.8-flash` (or another model confirmed as accessible to your key)
   - `APP_SECRET` = long random string, at least 32 random characters
   - `SETUP_TOKEN` = unique private setup code for creating the first admin
   - `COOKIE_SECURE` = `1`
   - `STORAGE_DIR` = `/data`
5. Deploy, generate a HTTPS domain, visit `/health`, then the website. During first setup, create admin using the `SETUP_TOKEN` (do not share it). Upload watermark via Admin.
6. Test one report and DOCX export. Approve only after verifying prices and charts against your broker's quote.

Railway domain is distinct from the previous project. **No accounts or reports from the old project are migrated automatically.**

## Run locally

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export APP_SECRET='local-long-unguessable-string'
export GEMINI_API_KEY='your-key'
uvicorn app:app --reload --port 8080
```

For local HTTP testing set `COOKIE_SECURE=0`. For production Railway set `COOKIE_SECURE=1`.

## APK from GitHub without Android Studio

1. In the new repository open **Actions → Build Gold Analyst Pro APK → Run workflow**.
2. After a green run, download artifact **GoldAnalystPro-debug-APK**. Extract it and install `app-debug.apk` on Android (permission to install apps from this source may be required).
3. On first launch, the app requests the **new** Railway HTTPS URL. Paste it to connect. The Android wrapper supports image uploads and authenticated downloads.
4. This is an **unsigned-for-release debug** APK intended for internal testing, not Play Store publication. Keep the repository private, and build/sign a release package before broad distribution.

No APK binary is shipped in this source ZIP. GitHub Actions must successfully compile it first.

## Operational / risk notes

- Gemini free-tier eligibility/availability may change; API quota errors 429 and demand spikes 503 can still occur. API spend and Railway hosting are separate.
- Screen images are **not live quotes**; results are scenarios, not confirmed market prices. Do not force trading advice or lot generation.
- Technical sentiment is not independently verified fundamental sentiment. Macro headlines are marked unverified without a data feed.
- Reviewer responsibility includes broker compliance, instrument alias matching (e.g. broker symbols may differ), screenshot timing, numeric levels, and image calibration.
- Avoid sending confidential client screenshots to free-tier APIs unless the applicable data terms are acceptable.
- Use strong secrets, HTTPS, Railway backups, and rotate passwords as needed. For production-scale teams migrate SQLite to a managed DB and external object storage.
