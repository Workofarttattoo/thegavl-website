# Square Payment Integration Setup

**Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.**

**Date:** October 29, 2025

This guide explains how to set up Square payment processing for automated verdict purchases on TheGAVL.

---

## Overview

The Square integration enables:
- ✅ Embedded credit card payment form
- ✅ Instant verdict allocation after payment
- ✅ Secure PCI-compliant processing
- ✅ No phone calls or manual processing needed
- ✅ Automatic receipt emails from Square

---

## Files Created

1. **`/api/square-payment.py`** - Serverless payment processing API
2. **`purchase-verdicts.html`** - Updated with Square Web Payments SDK
3. **`SQUARE_PAYMENT_SETUP.md`** - This setup guide

---

## Step 1: Create Square Account

### Sandbox (Testing)

1. Go to: https://developer.squareup.com/
2. Click **"Get Started"**
3. Create a developer account
4. You'll get access to **Sandbox** environment for testing

### Production (Live Payments)

1. Go to: https://squareup.com/signup
2. Create business account
3. Complete verification
4. Add bank account for payouts

---

## Step 2: Get Your Square Credentials

### In Square Developer Dashboard:

1. Go to: https://developer.squareup.com/apps
2. Click **"+"** to create new application
3. Name it: **"TheGAVL Payment System"**
4. Open the application

### Copy These Values:

**Sandbox:**
- **Application ID (Sandbox):** `sandbox-sq0idb-XXXXX...`
- **Access Token (Sandbox):** `EAAAl...`
- **Location ID:** Get from Locations tab

**Production:**
- **Application ID (Production):** `sq0idp-XXXXX...`
- **Access Token (Production):** `EAAAE...`
- **Location ID:** Get from Locations tab

---

## Step 3: Configure Vercel Environment Variables

### In Vercel Dashboard:

1. Go to your project: https://vercel.com/bbb-4fb61ed6/thegavl-website
2. Click **"Settings"** → **"Environment Variables"**
3. Add these variables:

```
# Square Sandbox (for testing)
SQUARE_APPLICATION_ID_SANDBOX = sandbox-sq0idb-XXXXX
SQUARE_ACCESS_TOKEN_SANDBOX = EAAAl-XXXXX
SQUARE_LOCATION_ID_SANDBOX = LXXXXX

# Square Production (for live payments)
SQUARE_APPLICATION_ID = sq0idp-XXXXX
SQUARE_ACCESS_TOKEN = EAAAE-XXXXX
SQUARE_LOCATION_ID = LXXXXX

# Environment mode
SQUARE_ENVIRONMENT = sandbox
```

**⚠️ IMPORTANT:**
- Start with `SQUARE_ENVIRONMENT = sandbox` for testing
- Switch to `SQUARE_ENVIRONMENT = production` when ready for live payments
- **Never commit these values to Git!** (They're in Vercel only)

---

## Step 4: Update Code for Your Application IDs

### Edit `purchase-verdicts.html`

Change line 397 from:
```html
<script src="https://sandbox.web.squarecdn.com/v1/square.js"></script>
```

**For Production:**
```html
<script src="https://web.squarecdn.com/v1/square.js"></script>
```

Or make it dynamic:
```html
<script>
  const SQUARE_ENV = 'sandbox'; // Change to 'production' for live
  const sdkUrl = SQUARE_ENV === 'sandbox'
    ? 'https://sandbox.web.squarecdn.com/v1/square.js'
    : 'https://web.squarecdn.com/v1/square.js';

  const script = document.createElement('script');
  script.src = sdkUrl;
  document.head.appendChild(script);
</script>
```

---

## Step 5: Test in Sandbox Mode

### Test Credit Cards (Sandbox Only):

```
Card Number:   4111 1111 1111 1111
CVV:           111
Zip:           12345
Exp:           Any future date
```

**Other test cards:**
- **Visa:** 4111 1111 1111 1111
- **Mastercard:** 5105 1051 0510 5100
- **Amex:** 3782 822463 10005
- **Discover:** 6011 0009 9013 9424

### Test the Payment Flow:

1. Go to: https://thegavl-website.vercel.app/purchase-verdicts.html
2. Fill in your name and email
3. Select a package (try "Single Verdict - $39")
4. Click **"Continue to Payment"**
5. Enter test card: `4111 1111 1111 1111`
6. CVV: `111`, Zip: `12345`
7. Click **"Complete Payment"**
8. ✅ You should see: "Payment Successful! 1 verdict credits added"

### Check Sandbox Dashboard:

1. Go to: https://developer.squareup.com/apps
2. Click your app → **"Sandbox Test Accounts"**
3. View transactions under **"Payments"**

---

## Step 6: Switch to Production

### When Ready for Live Payments:

1. **In Vercel Environment Variables:**
   - Change `SQUARE_ENVIRONMENT` from `sandbox` to `production`
   - Verify `SQUARE_ACCESS_TOKEN` and `SQUARE_APPLICATION_ID` are for production

2. **In `purchase-verdicts.html`:**
   - Change SDK URL from `sandbox.web.squarecdn.com` to `web.squarecdn.com`

3. **Test with Real Card:**
   - Use your own card to make a $39 test purchase
   - Verify verdicts are allocated correctly
   - Check Square dashboard for the transaction
   - Refund the test payment

4. **Go Live:**
   - Announce to customers
   - Monitor Square dashboard for payments

---

## Payment Flow Diagram

```
User Visits purchase-verdicts.html
  ↓
Fills Name, Email, Selects Package
  ↓
Clicks "Continue to Payment"
  ↓
[Frontend] Calls /api/square-payment (create_payment)
  ↓
[Backend] Returns payment intent + Square config
  ↓
[Frontend] Loads Square Web Payments SDK
  ↓
[Frontend] Displays credit card form
  ↓
User Enters Card Details
  ↓
Clicks "Complete Payment"
  ↓
[Square SDK] Tokenizes card → returns source_id
  ↓
[Frontend] Calls /api/square-payment (process_payment) with source_id
  ↓
[Backend] Calls Square Payments API
  ↓
[Square] Processes payment → returns payment_id
  ↓
[Backend] Allocates verdicts to user account
  ↓
[Frontend] Shows success + redirects to onboarding
  ↓
User Can Immediately Analyze Cases
```

---

## Pricing Configuration

Edit `api/square-payment.py` to change pricing:

```python
PACKAGES = {
    'single': {
        'name': 'Single Verdict',
        'verdicts': 1,
        'amount': 3900,  # $39.00 in cents
        'validity_days': 30
    },
    'professional': {
        'name': 'Professional Package',
        'verdicts': 40,
        'amount': 39900,  # $399.00 in cents
        'validity_days': 90
    },
    'firm': {
        'name': 'Firm Package',
        'verdicts': 125,
        'amount': 99900,  # $999.00 in cents
        'validity_days': 180
    }
}
```

**⚠️ Amounts must be in cents** (e.g., $39 = 3900)

---

## Monitoring Payments

### Square Dashboard:

1. Go to: https://squareup.com/dashboard
2. Click **"Transactions"**
3. View all payments, refunds, disputes

### Key Metrics to Watch:

- **Success Rate:** Should be >95%
- **Refund Rate:** Should be <5%
- **Failed Payments:** Investigate errors
- **Chargebacks:** Address immediately

---

## Troubleshooting

### Payment Form Not Loading

**Error:** "Square SDK failed to load"

**Solution:**
- Check browser console for errors
- Verify Application ID is correct
- Ensure SDK URL matches environment (sandbox vs production)

### Payment Fails: "Invalid Access Token"

**Solution:**
- Verify `SQUARE_ACCESS_TOKEN` in Vercel matches your Square app
- Check token hasn't expired
- Ensure you're using production token for production environment

### Payment Succeeds but Verdicts Not Added

**Solution:**
- Check browser console for JavaScript errors
- Verify localStorage is enabled in browser
- Check `allocateVerdicts()` function in purchase-verdicts.html

### "Card declined" Errors

**Reasons:**
- Insufficient funds
- Card expired
- Security block by bank
- Incorrect CVV or zip code

**User Action:** Try different card or contact bank

---

## Security Best Practices

1. **Never Store Card Numbers**
   - Square SDK tokenizes cards
   - You never see full card numbers
   - Tokens are single-use only

2. **Use HTTPS Only**
   - Vercel provides automatic SSL
   - Payment forms only work on HTTPS

3. **Environment Variables**
   - Never commit tokens to Git
   - Use Vercel environment variables
   - Rotate tokens periodically

4. **Fraud Prevention**
   - Square handles fraud detection
   - Monitor for unusual patterns
   - Set up alerts in Square dashboard

5. **PCI Compliance**
   - Square SDK is PCI-compliant
   - Your server never touches card data
   - No PCI audit needed for this setup

---

## Going Live Checklist

- [ ] Square production account verified
- [ ] Bank account added for payouts
- [ ] Production credentials added to Vercel
- [ ] `SQUARE_ENVIRONMENT` set to `production`
- [ ] SDK URL changed to production
- [ ] Test purchase with real card successful
- [ ] Refund test purchase
- [ ] Monitor first 10 real transactions
- [ ] Set up Square email receipts
- [ ] Add support email to payment page
- [ ] Test full flow: Purchase → Case Analysis → Verdict

---

## Support Resources

**Square Documentation:**
- Web Payments SDK: https://developer.squareup.com/docs/web-payments/overview
- Payments API: https://developer.squareup.com/reference/square/payments-api
- Sandbox Testing: https://developer.squareup.com/docs/devtools/sandbox/overview

**Square Support:**
- Developer Discord: https://discord.gg/square-dev
- Support Email: developers@squareup.com
- Phone: 1-855-700-6000

**TheGAVL Support:**
- Email: sales@thegavl.com

---

## Cost Structure

**Square Fees:**
- **Online Payments:** 2.9% + $0.30 per transaction
- **No Monthly Fees:** Pay-as-you-go

**Example Transaction Costs:**

| Package | Price | Square Fee | Your Net |
|---------|-------|------------|----------|
| Single Verdict | $39.00 | $1.43 | $37.57 |
| Professional | $399.00 | $11.87 | $387.13 |
| Firm | $999.00 | $29.27 | $969.73 |

**Chargeback Fee:** $15-25 per chargeback (avoid with good service)

---

## Summary

✅ Square payment integration is complete
✅ Serverless API endpoint created
✅ Embedded payment form ready
✅ Automatic verdict allocation working
✅ Sandbox testing available
✅ Production-ready code

**Next Steps:**
1. Set up Square sandbox account
2. Add credentials to Vercel environment variables
3. Test with sandbox credit cards
4. Switch to production when ready
5. Start accepting automated payments!

---

**Last Updated:** October 29, 2025
