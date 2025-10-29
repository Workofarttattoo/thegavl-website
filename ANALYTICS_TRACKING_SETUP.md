# TheGAVL Analytics & Tracking Setup

**Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.**

**Date:** October 29, 2025
**Status:** Partially Configured

---

## ✅ WHAT'S INSTALLED

### 1. **Google Tag Manager (GTM)** ✅ LIVE
- **Container ID:** GTM-PTHBBMZF
- **Installed on:**
  - ✅ index.html
  - ✅ onboarding.html
  - ✅ purchase-verdicts.html
  - ⏳ verdict-results.html (needs to be added)

### 2. **Conversion Tracking** ✅ LIVE
- **E-commerce purchases tracked** via GTM dataLayer
- **Tracks:**
  - Transaction ID
  - Purchase value
  - Package type
  - Currency (USD)
- **Events:**
  - `purchase` event fires on successful payment
  - Includes full e-commerce data

### 3. **Visit Counter API** ✅ CREATED
- **Endpoint:** `/api/track-visit`
- **Tracks:**
  - Total visits
  - Unique visitors
  - Page views per page
  - Daily statistics
  - Top pages
- **Features:**
  - In-memory storage (fast)
  - IP + User Agent hashing for unique visitors
  - CORS-enabled
  - GET endpoint for statistics

---

## ⏳ WHAT NEEDS TO BE CONFIGURED

### 1. **Facebook Pixel** - NOT CONFIGURED
**Status:** Code ready, pixel ID needed

**How to Set Up:**

1. **Create Facebook Pixel:**
   - Go to: https://business.facebook.com/events_manager
   - Click "Connect Data Sources" → "Web"
   - Click "Facebook Pixel" → "Connect"
   - Name it: "TheGAVL Website"
   - Copy your Pixel ID (looks like: `123456789012345`)

2. **Add Pixel ID to your pages:**
   - Edit these files:
     - `index.html`
     - `onboarding.html`
     - `purchase-verdicts.html`
     - `verdict-results.html`
   - Find: `fbq('init', 'YOUR_FACEBOOK_PIXEL_ID');`
   - Replace with: `fbq('init', '123456789012345');`

3. **Verify Installation:**
   - Install: Facebook Pixel Helper (Chrome extension)
   - Visit your site
   - Check that pixel fires correctly

**Events Tracked:**
- `PageView` - On every page
- `Purchase` - On successful payment (already coded)
- `Lead` - Can add for form submissions

---

### 2. **Google Analytics 4 (GA4)** - OPTIONAL
**Status:** Can use GTM or direct GA4

**Option A: Through GTM (Recommended)**
1. Go to: https://tagmanager.google.com
2. Open container: GTM-PTHBBMZF
3. Add New Tag → Google Analytics: GA4 Configuration
4. Enter your GA4 Measurement ID
5. Trigger: All Pages
6. Submit & Publish

**Option B: Direct Installation**
1. Create GA4 property: https://analytics.google.com
2. Get Measurement ID (looks like: `G-XXXXXXXXXX`)
3. Add to all pages in `<head>`:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

### 3. **Vercel Analytics** - OPTIONAL
**Status:** Not installed

Vercel offers built-in analytics for free:

1. Go to: https://vercel.com/bbb-4fb61ed6/thegavl-website
2. Click "Analytics" tab
3. Click "Enable Vercel Analytics"
4. Add to all pages:

```html
<script defer src="/_vercel/insights/script.js"></script>
```

**Benefits:**
- Real-time visitor data
- Page performance metrics
- No configuration needed
- Works immediately

---

## 📊 CURRENT TRACKING CAPABILITIES

### What You Can Track Now:

1. **Page Views** (GTM)
   - Which pages visitors view
   - Time spent on each page
   - Navigation flow

2. **Purchases** (GTM + Our Code)
   - Transaction value
   - Package purchased
   - Payment ID
   - User email (if you add to dataLayer)

3. **Form Submissions** (Can add)
   - Sign-up forms
   - Case submissions
   - Contact forms

4. **Button Clicks** (Can add via GTM)
   - "Analyze My Case" clicks
   - "Purchase" button clicks
   - External link clicks

---

## 🎯 RECOMMENDED TRACKING EVENTS

Add these events to track user behavior:

### 1. **Case Submission Started**
Add to onboarding.html when user starts filling form:

```javascript
if (window.dataLayer) {
    window.dataLayer.push({
        'event': 'case_submission_started',
        'case_type': caseType
    });
}
```

### 2. **Case Analysis Completed**
Add to verdict-results.html when results shown:

```javascript
if (window.dataLayer) {
    window.dataLayer.push({
        'event': 'case_analysis_completed',
        'case_type': caseType,
        'predicted_outcome': verdictResult.predicted_outcome,
        'confidence': verdictResult.confidence
    });
}
```

### 3. **Verdict Purchase Intent**
Add to purchase-verdicts.html when "Continue to Payment" clicked:

```javascript
if (window.dataLayer) {
    window.dataLayer.push({
        'event': 'begin_checkout',
        'value': selectedPackage.amount,
        'currency': 'USD',
        'items': [{
            'item_name': selectedPackage.name,
            'item_id': packageType,
            'price': selectedPackage.amount
        }]
    });
}
```

---

## 📈 ANALYTICS DASHBOARDS

### Google Tag Manager (GTM)
**URL:** https://tagmanager.google.com
**Container:** GTM-PTHBBMZF

**What to Monitor:**
- Tag firing status
- Trigger events
- Variables
- Debug mode for testing

### Facebook Events Manager
**URL:** https://business.facebook.com/events_manager

**What to Monitor:**
- Pixel status (active/inactive)
- Events received
- Conversion tracking
- Custom audiences

### Vercel Dashboard
**URL:** https://vercel.com/bbb-4fb61ed6/thegavl-website

**What to Monitor:**
- Deployment status
- Function logs
- Analytics (if enabled)
- Error tracking

---

## 🔍 HOW TO CHECK WHAT'S TRACKING

### Test Your Tracking:

1. **Install Browser Extensions:**
   - Google Tag Assistant (for GTM)
   - Facebook Pixel Helper (for FB Pixel)
   - GA Debugger (for Google Analytics)

2. **Visit Your Pages:**
   - https://thegavl-website.vercel.app/index.html
   - https://thegavl-website.vercel.app/onboarding.html
   - https://thegavl-website.vercel.app/purchase-verdicts.html

3. **Check Console:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - You should see GTM debug messages

4. **Check Network Tab:**
   - DevTools → Network tab
   - Filter by "gtm" or "analytics"
   - You should see requests to Google/Facebook

---

## 📋 VISIT COUNTER USAGE

### Get Current Statistics:

```bash
curl https://thegavl-website.vercel.app/api/track-visit
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_visits": 1234,
    "unique_visitors": 567,
    "page_views": {
      "TheGAVL - Quantum-Enhanced Legal AI": 500,
      "Purchase Verdicts - TheGAVL": 234,
      "TheGAVL Evidence Collection": 300
    },
    "top_pages": [
      ["TheGAVL - Quantum-Enhanced Legal AI", 500],
      ["TheGAVL Evidence Collection", 300],
      ["Purchase Verdicts - TheGAVL", 234]
    ]
  },
  "timestamp": "2025-10-29T12:00:00Z"
}
```

### Add Visit Tracking to Any Page:

Add this script before `</body>`:

```html
<script>
(function() {
    fetch('/api/track-visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            page: document.title,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            referrer: document.referrer || 'direct'
        })
    }).catch(err => console.log('Analytics error:', err));
})();
</script>
```

---

## 🎯 CONVERSION FUNNEL TRACKING

Track the complete customer journey:

### Funnel Stages:

1. **Landing** → Homepage visit
2. **Interest** → View pricing or modules
3. **Engagement** → Start case submission
4. **Trial** → Complete case analysis (trial)
5. **Intent** → Visit purchase page
6. **Conversion** → Complete payment

### Set Up in GTM:

1. Create Variables:
   - `pagePath`
   - `pageTitle`
   - `event`

2. Create Triggers:
   - Homepage View
   - Pricing Section View
   - Case Started
   - Case Completed
   - Purchase Page View
   - Purchase Completed (already done)

3. Create Tags:
   - GA4 Event for each stage
   - FB Custom Event for each stage

---

## 💰 ROI TRACKING

### Calculate Marketing ROI:

**Metrics to Track:**
- Cost per visitor (advertising spend / total visits)
- Conversion rate (purchases / visitors)
- Average order value
- Customer lifetime value

**Example Calculation:**

```
Advertising Spend: $1,000/month
Total Visitors: 5,000
Conversions: 100
Average Order Value: $399

Cost per Visitor = $1,000 / 5,000 = $0.20
Conversion Rate = 100 / 5,000 = 2%
Revenue = 100 × $399 = $39,900
ROI = ($39,900 - $1,000) / $1,000 = 3,890%
```

---

## ✅ QUICK START CHECKLIST

- [x] Google Tag Manager installed on key pages
- [x] Purchase conversion tracking configured
- [x] Visit counter API created
- [ ] Add GTM to verdict-results.html
- [ ] Get Facebook Pixel ID
- [ ] Install Facebook Pixel on all pages
- [ ] Test pixel with Facebook Pixel Helper
- [ ] Set up Google Analytics 4 (optional)
- [ ] Enable Vercel Analytics (optional)
- [ ] Test full conversion funnel
- [ ] Set up GTM triggers for custom events

---

## 🆘 TROUBLESHOOTING

### GTM Not Firing:

1. Check browser console for errors
2. Use GTM Preview mode: https://tagmanager.google.com
3. Verify container ID matches: GTM-PTHBBMZF
4. Check that script is in `<head>` section

### Facebook Pixel Not Tracking:

1. Verify Pixel ID is correct
2. Install Facebook Pixel Helper extension
3. Check browser console for `fbq is not defined` errors
4. Make sure pixel code is in `<head>` section

### Visit Counter Not Working:

1. Check Vercel function logs
2. Verify API endpoint exists: /api/track-visit
3. Check browser network tab for failed requests
4. Verify CORS headers are set correctly

---

## 📊 EXPECTED RESULTS

Once fully configured, you'll be able to track:

- **5,000+ page views/month** (estimated)
- **1,000+ unique visitors/month**
- **2-5% conversion rate** (100-250 purchases/month)
- **$39,900 - $99,750/month revenue**

All tracked in real-time across:
- Google Tag Manager
- Facebook Events Manager
- Your visit counter API
- Vercel analytics (if enabled)

---

## 🎉 SUMMARY

**What's Working Now:**
✅ Google Tag Manager on homepage, onboarding, and purchase pages
✅ Purchase conversion tracking with full e-commerce data
✅ Visit counter API tracking unique visitors and page views

**What to Add:**
⏳ Facebook Pixel (get pixel ID and add to pages)
⏳ GTM on verdict-results.html
⏳ Google Analytics 4 (optional)
⏳ Vercel Analytics (optional)

**Estimated Setup Time:**
- Facebook Pixel: 15 minutes
- Completing GTM setup: 5 minutes
- GA4 (optional): 20 minutes
- Testing everything: 30 minutes
- **Total: ~1 hour**

---

**Last Updated:** October 29, 2025
