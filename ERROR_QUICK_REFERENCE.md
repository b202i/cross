# API Error Quick Reference

## Common Errors and Solutions

### Quota Exceeded
```
======================================================================
  API Quota Exceeded: [provider]
======================================================================
```

**Cause:** You've used all your API credits/quota for this provider.

**Solution:**
1. Add credits at your provider dashboard (link shown in error message)
2. Or use a different provider: `--ai xai`, `--ai anthropic`, etc.

**Provider Dashboards:**
- Perplexity: https://www.perplexity.ai/settings/api
- OpenAI: https://platform.openai.com/settings/organization/billing
- Anthropic: https://console.anthropic.com/settings/billing
- xAI: https://console.x.ai/billing
- Gemini: https://console.cloud.google.com/billing

---

### Rate Limited
```
  Rate limit reached for [provider].
  Waiting 15s before retry...
```

**Cause:** Too many requests too quickly.

**Solution:** The system automatically retries with backoff. Just wait.

**If retries fail:** Wait a few minutes and try again.

---

### Service Unavailable
```
  [provider] service temporarily unavailable.
  Error: 503 Service Unavailable
```

**Cause:** Provider's API is temporarily down or overloaded.

**Solution:** 
1. System automatically retries (3 attempts)
2. If all retries fail, wait and try again later
3. Or use a different provider: `--ai <provider>`

---

## Switching Providers

All cross tools support the `--ai` flag:

```bash
# Use a different AI for generation
st-gen --ai anthropic prompt.prompt

# Use a different AI for merging
st-merge --ai openai file.json

# Use a different AI for fact-checking
st-fact --ai gemini file.json

# Use a different AI for fixing
st-fix --ai xai file.json
```

**Available providers:** xai, anthropic, openai, perplexity, gemini

---

## Free Tier Limits (approximate)

| Provider   | Free Tier                  | Notes                           |
|------------|----------------------------|---------------------------------|
| Perplexity | 5 requests/day             | Very limited                    |
| OpenAI     | Pay-as-you-go (no free)    | Must add payment method         |
| Anthropic  | Pay-as-you-go (no free)    | Must add payment method         |
| xAI (Grok) | Limited free tier          | Rate-limited                    |
| Gemini     | 60 requests/minute (free)  | Generous free tier              |

💡 **Tip:** Use Gemini for development/testing (best free tier). Use paid providers for production.

---

## Troubleshooting

### "No matching distribution found" during install
**Cause:** Python version incompatibility or missing dependency.

**Solution:** 
```bash
# Check Python version (need 3.11+)
python3 --version

# Reinstall in a fresh venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### "Module not found" errors
**Cause:** Not using the virtual environment.

**Solution:**
```bash
# Activate the venv
source .venv/bin/activate

# Or use the full path
/path/to/cross/.venv/bin/st-gen ...
```

### API key not found
**Cause:** Environment variable not set.

**Solution:**
```bash
# Add to your .zshrc or .bash_profile
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export XAI_API_KEY="xai-..."
export PERPLEXITY_API_KEY="pplx-..."
export GOOGLE_API_KEY="AIza..."

# Reload
source ~/.zshrc
```

---

## Getting Help

1. **Check error message** — It usually tells you exactly what to do
2. **Read documentation** — `README_*.md` files cover most scenarios
3. **Check provider status** — Visit provider's status page
4. **GitHub issues** — https://github.com/[username]/cross/issues
5. **Feedback** — Submit via GitHub issues or crossai.dev

---

## Error Message Format

All cross tools now provide structured, friendly error messages:

```
======================================================================
  [Error Title]
======================================================================

  [Clear explanation of what went wrong]

  [Numbered steps to fix the problem]

  [Additional context or alternatives]
======================================================================
```

**No more confusing stack traces!** 🎉

---

**Last updated:** March 16, 2026

