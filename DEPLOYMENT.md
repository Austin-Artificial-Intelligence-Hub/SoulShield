# Deployment Guide

## Quick Deploy (Recommended)

### Option 1: Vercel (Easiest)

1. **Install Vercel CLI** (if not already):
   ```bash
   npm i -g vercel
   ```

2. **Navigate to web folder and deploy**:
   ```bash
   cd web
   vercel
   ```

3. **Follow prompts**:
   - Link to existing project? **No**
   - What's your project name? **soulshield**
   - Which directory? **.** (current)
   - Override settings? **No**

4. **Production deploy**:
   ```bash
   vercel --prod
   ```

Your site will be live at `https://soulshield.vercel.app` (or custom name)

---

### Option 2: Netlify

1. **Install Netlify CLI** (if not already):
   ```bash
   npm i -g netlify-cli
   ```

2. **Navigate to web folder and deploy**:
   ```bash
   cd web
   netlify deploy
   ```

3. **Follow prompts**:
   - Create new site? **Yes**
   - Site name: **soulshield** (or your choice)
   - Deploy directory: **.** (current)

4. **Production deploy**:
   ```bash
   netlify deploy --prod
   ```

Your site will be live at `https://soulshield.netlify.app`

---

## Configuration Files Included

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel config with security headers |
| `netlify.toml` | Netlify config with security headers |

Both include proper CSP headers for security.

---

## Backend

The backend (AWS Lambda + API Gateway + DynamoDB) is already deployed at:
```
https://pypwr35xf3.execute-api.us-east-1.amazonaws.com/prod
```

The frontend is pre-configured to connect to this API.

---

## After Deployment

1. **Test the live site**:
   - Open your deployed URL
   - Register a new account
   - Send test messages
   - Verify voice features work
   - Test dark mode toggle

2. **Share the URL**:
   - Add to your hackathon submission
   - Include in demo video

---

## Custom Domain (Optional)

### Vercel
```bash
vercel domains add yourdomain.com
```

### Netlify
```bash
netlify domains add yourdomain.com
```

---

## Troubleshooting

**CORS errors?**
- The backend already allows all origins (`*`)
- If issues persist, check browser console

**API Key exposed?**
- The API key is rate-limited and scoped
- For production, implement proper auth flow

**Voice not working?**
- Requires HTTPS (both Vercel and Netlify provide this)
- Check browser microphone permissions
