# Deploying the Study Website (Supabase + Vercel / Render)

To host the study online and collect data from participants across devices, you need:

1. **Supabase** (free PostgreSQL database) so all participant data is safely collected in the cloud.
2. **Vercel** or **Render** (free hosting) to host the website.

---

## 1. Database: Supabase Setup

### Step 1: Create a Supabase Project
1. Go to [https://supabase.com](https://supabase.com) and sign in (or sign up for free).
2. Click **New Project**.
3. Choose a project name (e.g. `beyond-clicks-study`), set a strong database password (keep this safe), and pick a region close to your participants (e.g. `Singapore (ap-southeast-1)` or `Mumbai (ap-south-1)`).
4. Click **Create new project**.

### Step 2: Get your Database Connection String
1. In your Supabase dashboard, go to **Project Settings** (gear icon) → **Database**.
2. Scroll to **Connection parameters** or **Connection string**.
3. Select the **URI** tab.
4. Supabase offers two connection modes:
   - **Connection Pooler (Recommended for Vercel/Render):**
     - Select **Mode: Transaction** (port 6543) or **Mode: Session** (port 5432).
     - Copy the URI string:
       `postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
   - **Direct connection:**
     - `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`
5. Replace `[YOUR-PASSWORD]` with your real database password. Ensure `?sslmode=require` is at the end.

### Step 3: Migrate Local Data and Pilot Freeze (Optional but Recommended)
The app includes a built-in migration script to transfer all pilot participants (P01–P06) and the frozen pilot settings directly into Supabase:

```powershell
.venv\Scripts\python scripts/migrate_to_supabase.py "postgresql://postgres.[YOUR-PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
```

> **Note:** If you deploy without running the migration script, the app will automatically seed the frozen pilot analysis and locked threshold from `app/data/frozen_seed.json`, so the Main Study is immediately ready and unlocked.

---

## 2. Option A: Deploy to Vercel (Recommended - No Sleep / Cold Idle)

Vercel provides fast global edge routing and serverless function execution on their free tier.

### Step 1: Push Code to GitHub
Ensure your repository is pushed to your GitHub account:
```powershell
git add .
git commit -m "Configure Supabase and Vercel deployment with frozen pilot"
git push
```

### Step 2: Import Project on Vercel
1. Go to [https://vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New...** → **Project**.
3. Select your repository.
4. In **Project Settings**:
   - Framework Preset: **Other** (detected automatically via `vercel.json`).
   - Root Directory: `./` (leave default).

### Step 3: Add Environment Variables
Under **Environment Variables**, add:

| Key | Value |
| --- | --- |
| `DATABASE_URL` | Your Supabase connection URI (from Step 1) |
| `ADMIN_PASSWORD` | Password for the researcher dashboard (`/admin`) |
| `SECRET_KEY` | A random 32+ character string for signing session cookies |
| `GEMINI_API_KEY` | Your Google Gemini API key (optional, fallback provided) |
| `GROQ_API_KEY` | Your Groq API key (optional) |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` |

### Step 4: Deploy
1. Click **Deploy**.
2. Once complete, Vercel gives you a public domain (e.g. `https://beyond-clicks-study.vercel.app`).
3. Open the URL to verify:
   - Participants see the **Main study** button unlocked and ready ("Active Now").
   - The **Pilot study** is marked as "Completed & Frozen".
   - Open `<URL>/admin` and log in with `ADMIN_PASSWORD` to inspect data and monitor incoming participants in real time.

---

## 3. Option B: Deploy to Render

Render runs a dedicated container service using the existing `render.yaml`.

1. Go to [https://render.com](https://render.com) and sign in.
2. Click **New +** → **Blueprint** and select your repository.
3. Fill in the environment variables:
   - `DATABASE_URL`: Your Supabase connection string.
   - `ADMIN_PASSWORD`: Your chosen admin password.
   - `GEMINI_API_KEY` / `GROQ_API_KEY`: API keys for LLM assistance.
4. Click **Apply**.
5. Your service will be live at `https://beyond-clicks-study.onrender.com`.

*(Note: On Render's free tier, containers sleep after 15 minutes of inactivity and take ~50 seconds to spin up on the first visit. Vercel does not sleep.)*

---

## 4. Testing & Verification

1. **Verify Database Connection:**
   Visit your deployed website URL. The page should load immediately.
2. **Check Admin Dashboard:**
   Visit `/admin`, enter your `ADMIN_PASSWORD`, and verify:
   - Settings show: **Settings frozen** (Threshold: 1.75).
   - Go to **Backups & tools** → click **Check the AI providers** to verify LLM keys.
3. **Participant Flow:**
   Click **Start main study**. You should receive a code like `M01` and proceed into the experiment.
