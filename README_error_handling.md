# API Error Handling — Design & Implementation

## Overview

cross tools interact with multiple AI API providers (xAI, Anthropic, OpenAI, Perplexity, Gemini). Each provider can return various errors related to quotas, rate limits, service availability, and network issues. Users should receive clear, actionable error messages instead of raw stack traces.

**Design goal:** Graceful error handling across all tools with consistent, user-friendly messages.

---

## Common API Error Types

### 1. Quota/Billing Errors (HTTP 401, 429 with billing keywords)
**Symptoms:**
- "You exceeded your current quota"
- "insufficient_quota"
- "spending limit reached"
- "credits exhausted"

**User action required:**
- Add credits/upgrade billing plan
- Switch to a different AI provider

**System response:**
- Display clear message with dashboard URL
- Suggest alternative providers
- Exit immediately (no retry)

### 2. Rate Limiting (HTTP 429 without billing keywords)
**Symptoms:**
- "429 too many requests"
- "rate limit exceeded"
- "try again later"

**User action:**
- Usually none — system handles automatically

**System response:**
- Retry with exponential backoff (3 attempts)
- Wait 15s, 30s, 60s between retries

### 3. Transient Service Errors (HTTP 500, 503, 504)
**Symptoms:**
- "503 service unavailable"
- "500 internal server error"
- "temporarily unavailable"
- "high demand"

**User action:**
- Usually none — wait and retry

**System response:**
- Retry with backoff (3 attempts)
- If all retries fail, display error and suggest trying later

### 4. Network/Unknown Errors
**Symptoms:**
- Connection timeouts
- DNS failures
- Unexpected API changes

**User action:**
- Check network connection
- Check provider status page
- Report to maintainers if persistent

**System response:**
- Display error message
- Suggest checking network/provider status
- Exit with error code

---

## Implementation

### Core Module: `ai_error_handler.py`

Centralized error handling logic used by all cross tools.

**Key functions:**

```python
# Error classification
get_error_type(error) → "quota" | "rate_limit" | "transient" | "other"
is_quota_error(error) → bool
is_rate_limit_error(error) → bool
is_transient_error(error) → bool

# User-facing messages
format_quota_error_message(ai_name, script_name) → str
format_rate_limit_message(ai_name, wait_seconds) → str
format_transient_error_message(ai_name, error) → str

# Orchestration
handle_api_error(error, ai_name, script_name, exit_on_quota, quiet) → error_type
retry_with_backoff(func, ai_name, max_retries, wait_seconds, quiet, script_name)
```

### Integration Point: `ai_handler.py`

The `process_prompt()` function is the single point where all AI API calls flow through. It now wraps API calls in try-except and delegates error handling to `ai_error_handler`.

**Before:**
```python
def process_prompt(ai_key, prompt, verbose, use_cache):
    handler_cls = AI_HANDLER_REGISTRY.get(ai_key)
    payload = handler_cls.get_payload(prompt)
    client = handler_cls.get_client()
    response, was_cached = handler_cls.get_cached_response(...)
    return AIResponse(payload, client, response, model, was_cached)
```

**After:**
```python
def process_prompt(ai_key, prompt, verbose, use_cache):
    handler_cls = AI_HANDLER_REGISTRY.get(ai_key)
    try:
        payload = handler_cls.get_payload(prompt)
        client = handler_cls.get_client()
        response, was_cached = handler_cls.get_cached_response(...)
        return AIResponse(payload, client, response, model, was_cached)
    except Exception as e:
        handle_api_error(e, ai_key, exit_on_quota=True, quiet=False)
        raise  # Re-raise if handle_api_error didn't exit
```

**Result:** All scripts (`st-gen`, `st-merge`, `st-fact`, `st-fix`, `st-bang`, etc.) automatically get graceful error handling with zero additional code.

---

## Error Messages — Before and After

### Before (raw stack trace)
```
Traceback (most recent call last):
  File "/Users/Matt/github/cross/.venv/bin/st-merge", line 844, in <module>
    main()
  File "/Users/Matt/github/cross/.venv/bin/st-merge", line 661, in main
    process_prompt(args.ai, prompt, args.verbose, args.cache))
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/Matt/github/cross/ai_handler.py", line 73, in process_prompt
    cached_response, was_cached = handler_cls.get_cached_response(...)
  ... 15 more lines ...
openai.AuthenticationError: Error code: 401 - {'error': {'message': 
'You exceeded your current quota, please check your plan and billing 
details. For more information, visit https://www.perplexity.ai/settings/api.',
'type': 'insufficient_quota', 'code': 401}}
```

**Problems:**
- User must read 20+ lines to find the actual issue
- No clear action to take
- Stack trace is intimidating to non-developers

### After (user-friendly)
```
======================================================================
  API Quota Exceeded: perplexity
======================================================================

  You have exceeded your API quota or billing limit for perplexity.

  To continue:
    1. Check your billing and add credits at:
       https://www.perplexity.ai/settings/api

    2. Or use a different AI provider with:
       st-merge --ai <provider> ...

  Available providers: xai, anthropic, openai, perplexity, gemini
======================================================================
```

**Benefits:**
- Clear, concise explanation
- Direct link to fix the problem
- Actionable alternatives
- No intimidating stack trace

---

## Retry Strategy

The system distinguishes between errors worth retrying and errors that are permanent.

### Retry-able Errors
- Rate limits (429 without billing keywords)
- Transient service errors (503, 500, 502, 504)
- Temporary overload messages

**Strategy:**
```
Attempt 1 → fail → wait 15s
Attempt 2 → fail → wait 30s (exponential backoff)
Attempt 3 → fail → give up, show error
```

### Non-retry-able Errors
- Quota exhausted
- Billing issues
- Invalid API keys
- Authentication failures

**Strategy:**
```
Attempt 1 → fail → show clear error → exit immediately
```

---

## Tool-Specific Behavior

### Simple Tools (st-gen, st-read, st-cat)
**Behavior:** Exit immediately on any error after showing message.

**Reason:** These tools perform a single AI call. No point retrying — user can just run the command again.

### Batch Tools (st-bang, st-cross)
**Behavior:** 
- Skip the failed AI
- Continue with remaining AI
- Show summary of successes/failures at the end

**Reason:** If 1 of 5 AI hits quota, the other 4 can still complete.

**Future enhancement (not yet implemented):**
- Detect quota error during batch
- Prompt user: "Skip perplexity and continue with remaining 4 AI? (y/n)"

### Interactive Tools (st-fix --mode iterate)
**Behavior:**
- Try current AI
- On quota error, automatically try next AI in rotation
- Continue until claim is fixed or all AI exhausted

**Reason:** st-fix iterates through all 5 AI by design. If one hits quota, just move to the next.

**Implementation note:** `st-fix.py` already has custom retry logic. This needs to be refactored to use `ai_error_handler` for consistency.

---

## Provider-Specific Notes

### Perplexity
- Free tier: 5 requests/day (very limited)
- Quota errors are common for new users
- Dashboard: https://www.perplexity.ai/settings/api

### OpenAI
- Pay-as-you-go with usage limits
- Errors: "You exceeded your current quota" or "insufficient_quota"
- Dashboard: https://platform.openai.com/settings/organization/billing

### Anthropic
- Credits-based system
- Errors: "credit balance is too low"
- Dashboard: https://console.anthropic.com/settings/billing

### xAI (Grok)
- Free tier available
- Rate limits on free tier
- Dashboard: https://console.x.ai/billing

### Gemini (Google)
- Free tier: 60 requests/minute
- Errors: "RESOURCE_EXHAUSTED" or "quota exceeded"
- Dashboard: https://console.cloud.google.com/billing

---

## Testing Error Handling

### Manual Testing
```bash
# Exhaust your quota for a provider (e.g., perplexity)
# Then run any command that uses that provider:
st-gen --ai perplexity test.prompt

# Expected: Clean error message with dashboard URL and alternatives
```

### Simulated Testing
```python
# In ai_perplexity.py (temporary test code):
def get_cached_response(...):
    # Simulate quota error
    raise Exception("Error code: 401 - insufficient_quota")
```

### Unit Testing (future)
```python
# tests/test_error_handler.py
def test_quota_error_detection():
    error = Exception("You exceeded your current quota")
    assert is_quota_error(error) == True
    assert get_error_type(error) == "quota"

def test_rate_limit_error_detection():
    error = Exception("429 too many requests")
    assert is_rate_limit_error(error) == True
    assert get_error_type(error) == "rate_limit"
```

---

## Future Enhancements

### 1. Quota Pre-Check (proactive)
Before starting a long batch job (`st-bang`, `st-cross`), ping each AI with a minimal request to verify quota is available.

**Benefit:** Fail fast instead of 30 minutes into a 5-AI batch job.

```python
def check_quota(ai_name):
    """Verify AI is available before starting batch job."""
    try:
        process_prompt(ai_name, "test", verbose=False, use_cache=False)
        return True
    except QuotaError:
        return False
```

### 2. Cost Estimation
Show estimated token count and cost before expensive operations.

```python
st-merge --dry-run file.json
# → Estimated tokens: 45,000
# → Estimated cost: $0.90 (perplexity)
# → Proceed? (y/n)
```

### 3. Auto-Fallback in Batch Mode
If an AI fails mid-batch, automatically substitute another provider.

```python
st-bang --fallback file.json
# → perplexity failed (quota)
# → auto-fallback to openai
# → Results: xai, anthropic, openai (fallback), gemini
```

### 4. Retry Queue for Rate Limits
For batch jobs, queue rate-limited requests and process them after cooldown.

```python
# Internal:
# - Rate limit hit on perplexity at request 3/10
# - Queue remaining 7 requests
# - Process xai, anthropic, openai, gemini first
# - Return to perplexity queue after 60s cooldown
```

---

## Refactoring Checklist

### Phase 1: Core Error Handler ✓
- [x] Create `ai_error_handler.py`
- [x] Implement error classification functions
- [x] Implement message formatting functions
- [x] Add retry_with_backoff orchestration
- [x] Test error classification and messages

### Phase 2: Integrate with ai_handler.py ✓
- [x] Wrap `process_prompt()` in try-except
- [x] Call `handle_api_error()` on exceptions
- [x] Verify all scripts get automatic error handling
- [x] Test with real quota error

### Phase 3: Refactor st-fix.py (in progress)
- [ ] Replace custom retry logic with `retry_with_backoff()`
- [ ] Use `ai_error_handler` for iterate mode
- [ ] Use `ai_error_handler` for synthesize mode
- [ ] Remove duplicate error-detection code (PERMANENT_429, TRANSIENT)

### Phase 4: Enhance Batch Tools
- [ ] st-bang: skip failed AI, continue with rest
- [ ] st-cross: skip failed AI, continue with rest
- [ ] Show per-AI status in summary table (done/failed/quota)

### Phase 5: Documentation
- [x] Create README_error_handling.md
- [ ] Update README.md with error handling section
- [ ] Add troubleshooting guide for common errors
- [ ] Document provider quota limits and free tiers

---

## Summary

| Before | After |
|--------|-------|
| Raw stack traces | Clear, actionable messages |
| Manual retry required | Automatic retry with backoff |
| Inconsistent error handling | Centralized, uniform behavior |
| No guidance on alternatives | Suggests other providers and links to dashboards |
| Developer-focused | User-focused |

**Key principle:** Users should never see a stack trace for common, expected errors like quota limits and rate limiting. They should get clear guidance on what to do next.

