# Error Handling — User Experience Comparison

## Example: Quota Error in st-merge

### Before (without graceful error handling)

```bash
$ st-merge --quality rabbit-r1-2026.json

Executing command: st-merge --quality  rabbit-r1-2026.json
  Story 1: xai/grok-4-1-fast-reasoning  score: 0.55
  Story 2: openai/gpt-4o  score: 0.34
  Story 3: perplexity/sonar-pro  score: 1.03
  Story 4: gemini/gemini-2.5-flash  score: 0.88

  Mode: quality (fact-check data found — claims)
  Base story: 3  (perplexity/sonar-pro  avg score: 1.03)
  Synthesizer: perplexity (base story author)

  Building verdict-annotated prompt...
  Calling perplexity to synthesize 4 stories...

Traceback (most recent call last):
  File "/Users/Matt/github/cross/.venv/bin/st-merge", line 844, in <module>
    main()
  File "/Users/Matt/github/cross/.venv/bin/st-merge", line 661, in main
    process_prompt(args.ai, prompt, args.verbose, args.cache))
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/Matt/github/cross/ai_handler.py", line 73, in process_prompt
    cached_response, was_cached = handler_cls.get_cached_response(...)
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/Matt/github/cross/ai_perplexity.py", line 78, in get_cached_response
    return get_perplexity_cached_response(client, payload, verbose, use_cache)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/Matt/github/cross/ai_perplexity.py", line 133, in get_perplexity_cached_response
    response = client.chat.completions.create(**payload)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../openai/_utils/_utils.py", line 279, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File ".../openai/resources/chat/completions/completions.py", line 914, in create
    return self._post(
           ^^^^^^^^^^^
  File ".../openai/_base_client.py", line 1242, in post
    return cast(ResponseT, self.request(...))
                           ^^^^^^^^^^^^^^^^^
  File ".../openai/_base_client.py", line 919, in request
    return self._request(
           ^^^^^^^^^^^^^^
  File ".../openai/_base_client.py", line 1023, in _request
    raise self._make_status_error_from_response(err.response) from None
openai.AuthenticationError: Error code: 401 - {'error': {'message': 
'You exceeded your current quota, please check your plan and billing 
details. For more information, visit https://www.perplexity.ai/settings/api.',
'type': 'insufficient_quota', 'code': 401}}
```

**Problems:**
- 30+ lines of confusing stack trace
- User must dig through technical jargon to find the issue
- No clear action to take
- Intimidating to non-developers
- User doesn't know if this is their fault or a bug

---

### After (with graceful error handling)

```bash
$ st-merge --quality rabbit-r1-2026.json

Executing command: st-merge --quality  rabbit-r1-2026.json
  Story 1: xai/grok-4-1-fast-reasoning  score: 0.55
  Story 2: openai/gpt-4o  score: 0.34
  Story 3: perplexity/sonar-pro  score: 1.03
  Story 4: gemini/gemini-2.5-flash  score: 0.88

  Mode: quality (fact-check data found — claims)
  Base story: 3  (perplexity/sonar-pro  avg score: 1.03)
  Synthesizer: perplexity (base story author)

  Building verdict-annotated prompt...
  Calling perplexity to synthesize 4 stories...

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
- Actionable alternative (use different AI)
- Professional, not intimidating
- User understands this is expected behavior, not a bug

---

## Example: Rate Limit Error with Auto-Retry

### Before

```bash
$ st-gen test.prompt

Traceback (most recent call last):
  File "/Users/Matt/github/cross/.venv/bin/st-gen", line 123, in <module>
    main()
  ...
openai.RateLimitError: Error code: 429 - {'error': {'message': 
'Rate limit reached for requests', 'type': 'requests', 
'param': None, 'code': 'rate_limit_exceeded'}}
```

User must manually retry the command.

---

### After

```bash
$ st-gen test.prompt

Calling xai to generate story...

  Rate limit reached for xai.
  Waiting 15s before retry...

  Retry 1/3 in 15s...

Calling xai to generate story...
✓ Story generated successfully.
```

**Benefits:**
- Automatic retry with backoff
- User sees progress, knows system is handling it
- No manual intervention required
- Success after retry

---

## Example: Transient Service Error

### Before

```bash
$ st-fact file.json

Traceback (most recent call last):
  ...
requests.exceptions.HTTPError: 503 Server Error: Service Unavailable
```

---

### After

```bash
$ st-fact file.json

Calling anthropic for fact-check...

  anthropic service temporarily unavailable.
  Error: 503 Service Unavailable

  Retry 1/3 in 15s...

Calling anthropic for fact-check...

  anthropic service temporarily unavailable.
  Error: 503 Service Unavailable

  Retry 2/3 in 30s...

Calling anthropic for fact-check...
✓ Fact-check complete.
```

**Benefits:**
- Clear status updates
- Automatic retry with increasing backoff
- User knows what's happening
- Success message on completion

---

## Example: Batch Job with Mixed Results

This scenario is not yet implemented, but shows the future direction:

```bash
$ st-bang file.json

  AI Make       Model                   Status       Elapsed
  ──────────────────────────────────────────────────────────
  xai           grok-4-1-fast-reasoning   done        00:02  
  anthropic     claude-opus-4-5          done        00:45  
  openai        gpt-4o                   done        00:23  
  perplexity    sonar-pro                QUOTA       --     
  gemini        gemini-2.5-flash         done        00:22  
  ──────────────────────────────────────────────────────────

  Results: 4 done  0 failed  1 quota

  Note: perplexity was skipped due to quota limit.
        Add credits at: https://www.perplexity.ai/settings/api
```

**Benefits:**
- Batch continues despite one failure
- Clear status for each AI
- Helpful note at the end
- 4 out of 5 results still obtained

---

## Developer Note

The error handler is completely transparent to most of the codebase. Once integrated into `ai_handler.py`, all tools (`st-gen`, `st-merge`, `st-fact`, `st-fix`, `st-bang`, etc.) automatically benefit from graceful error handling with zero code changes.

**Implementation locations:**
- `ai_error_handler.py` — Core error handling logic
- `ai_handler.py` — Integration point (process_prompt wrapper)
- Each `st-*.py` tool — No changes needed (automatic)

**Exception:** `st-fix.py` has custom retry logic that should be refactored to use the centralized error handler for consistency.

