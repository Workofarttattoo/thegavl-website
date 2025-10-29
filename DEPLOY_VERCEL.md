# Deploy TheGAVL to Vercel (Serverless API + Static Site)

**Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.**

This guide shows how to deploy TheGAVL website + API to Vercel for free.

---

## What This Does

Deploys your entire TheGAVL website to **thegavl.com** with:
- ✅ All static pages (HTML/CSS/JS)
- ✅ Serverless API at `/api/predict`
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Zero server management
- ✅ **100% FREE** (for hobby projects)

---

## Prerequisites

1. GitHub account (you already have this)
2. Vercel account (free - sign up with GitHub)

---

## Step-by-Step Deployment

### 1. Sign Up for Vercel

Visit: **https://vercel.com/signup**

- Click "Continue with GitHub"
- Authorize Vercel to access your repositories
- No credit card required

### 2. Import Your Repository

1. Go to: **https://vercel.com/new**
2. Click "Import Project"
3. Find and select: **Workofarttattoo/thegavl-website**
4. Click "Import"

### 3. Configure Project

Vercel will auto-detect your setup. Just confirm:

- **Framework Preset**: Other (or None)
- **Root Directory**: `./`
- **Build Command**: (leave empty)
- **Output Directory**: (leave empty)

### 4. Add Custom Domain

1. After deployment, go to Project Settings → Domains
2. Add your domain: **thegavl.com**
3. Follow Vercel's DNS instructions:

**If using GoDaddy:**
```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

4. Wait 5-10 minutes for DNS propagation
5. Vercel will automatically provision SSL certificate

### 5. Deploy!

Click **"Deploy"**

Vercel will:
- Build your site (instant - it's static HTML)
- Deploy serverless API function
- Assign you a URL: `https://thegavl-website.vercel.app`
- Set up thegavl.com when DNS is ready

---

## How It Works

### File Structure

```
thegavl-website/
├── index.html              # Landing page
├── onboarding.html         # Case submission
├── verdict-results.html    # Results display
├── purchase-verdicts.html  # Purchase flow
├── api/
│   └── predict.py          # Serverless API function
├── vercel.json             # Vercel configuration
└── requirements.txt        # Python dependencies
```

### API Endpoint

After deployment, your API is available at:
```
https://thegavl.com/api/predict
```

No separate server needed!

### How Serverless Works

1. User submits case on thegavl.com/onboarding.html
2. JavaScript calls `/api/predict` (same domain)
3. Vercel spins up Python function on-demand
4. Function runs prediction logic
5. Returns JSON response in ~100-300ms
6. Function shuts down after response

**Cost:** $0 (free tier includes 100GB bandwidth + 100,000 function invocations/month)

---

## Testing Locally

### Test the API Function

```bash
cd /Users/noone/thegavl-website

# Test directly
python3 api/predict.py
```

### Test with a Request

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "TEST-001",
    "case_name": "Test Case",
    "issue_area": "constitutional",
    "opinion_text": "Strong evidence supports petitioner",
    "petitioner": "John Doe",
    "respondent": "State"
  }'
```

---

## Updating After Deployment

Every time you push to GitHub, Vercel auto-deploys:

```bash
cd /Users/noone/thegavl-website
git add .
git commit -m "Update website"
git push
```

Vercel will:
1. Detect the push
2. Rebuild your site
3. Deploy in ~30 seconds
4. Your site is live!

---

## Environment Variables (Optional)

If you need secrets (API keys, database URLs):

1. Go to Vercel Dashboard → Project → Settings → Environment Variables
2. Add variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - etc.

3. Access in Python:
```python
import os
supabase_url = os.environ.get('SUPABASE_URL')
```

---

## Monitoring

### View Logs

1. Go to Vercel Dashboard → Your Project
2. Click on a deployment
3. View "Functions" tab to see API logs

### View Analytics

1. Dashboard → Analytics
2. See:
   - Page views
   - API calls
   - Response times
   - Bandwidth usage

---

## Troubleshooting

### API Returns 500 Error

Check function logs in Vercel dashboard:
1. Click on deployment
2. Functions tab
3. Click on `/api/predict`
4. View runtime logs

### CORS Errors

The `vercel.json` file already configures CORS. If you still see errors, ensure:
1. Headers are set in `vercel.json`
2. Redeploy after changes
3. Clear browser cache

### DNS Not Propagating

Wait 5-60 minutes. Check status:
```bash
dig thegavl.com
```

Should show Vercel's IP: `76.76.21.21`

### Function Times Out

Vercel hobby plan: 10 second timeout
Vercel pro plan: 60 second timeout

Your predictions are ~100-300ms, so you're fine.

---

## Cost Breakdown

### Free Tier (Hobby)
- ✅ 100GB bandwidth/month
- ✅ 100,000 function invocations/month
- ✅ Unlimited sites
- ✅ Custom domains
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Instant rollbacks

**Realistic usage:**
- If each case analysis is ~1MB total
- You can handle **100,000 case analyses/month for FREE**

### Pro Tier ($20/month)
Only needed if you exceed free tier:
- 1TB bandwidth
- 1,000,000 function invocations
- Analytics dashboard
- Password protection
- Team features

---

## Advantages Over Traditional Hosting

| Feature | Traditional Server | Vercel Serverless |
|---------|-------------------|-------------------|
| Setup time | Hours/days | 5 minutes |
| Cost | $5-50/month | $0 |
| Scaling | Manual | Automatic |
| SSL | Manual setup | Automatic |
| CDN | Extra cost | Included |
| Deployment | Manual FTP/SSH | Git push |
| Downtime | Hours during updates | Zero |
| Maintenance | You manage | Vercel manages |

---

## Alternative Platforms

If you don't want Vercel:

### Netlify (Similar to Vercel)
1. Connect GitHub repo
2. Add `netlify.toml`:
```toml
[build]
  functions = "api"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### Cloudflare Pages + Workers
1. Deploy static site to Pages
2. Deploy API as Cloudflare Worker
3. Free: 100,000 requests/day

### Railway.app
1. Connect GitHub
2. Auto-deploys full Python app
3. Free: $5/month credit

---

## What Happens Next

After deploying to Vercel:

1. **Users visit:** thegavl.com/onboarding.html
2. **Fill out case:** All 8 steps
3. **Click submit:** JavaScript calls `/api/predict`
4. **Vercel spins up:** Python function runs
5. **5 models analyze:** Ensemble prediction generated
6. **Results returned:** JSON with verdict
7. **Display results:** verdict-results.html shows outcome
8. **Function shuts down:** No ongoing costs

**Total time:** 100-300ms per case analysis

---

## Security Notes

1. **Rate Limiting:** Add to prevent abuse
```python
# In api/predict.py
MAX_REQUESTS_PER_MINUTE = 10
# Implement with Redis or Vercel KV
```

2. **Input Validation:** Already included
3. **CORS:** Configured in vercel.json
4. **HTTPS:** Automatic with Vercel
5. **DDoS Protection:** Vercel handles this

---

## Quick Reference Commands

```bash
# Check if deployed correctly
curl https://thegavl.com/api/predict -X POST \
  -H "Content-Type: application/json" \
  -d '{"case_id":"test","case_name":"test","issue_area":"test","opinion_text":"test"}'

# View Vercel CLI status
npx vercel --version

# Deploy from command line
npx vercel deploy

# View logs
npx vercel logs
```

---

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Serverless Functions:** https://vercel.com/docs/functions
- **Custom Domains:** https://vercel.com/docs/custom-domains

---

## Summary

✅ Your GAVL API is now part of your website
✅ No separate server to manage
✅ Scales automatically
✅ Costs $0 for first 100K analyses/month
✅ Deploy with one `git push`
✅ Available at https://thegavl.com/api/predict

**Ready to deploy? Go to: https://vercel.com/new**

---

**Last Updated:** October 29, 2025
