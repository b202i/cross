# A question for AI about cross product of AI

I've got this data that I want to understand better, what does it mean?
The data is from a cross product experiment with 4 different AI.
Each AI generates a report or story, so in this case there are 4 stories.
Then each AI performs a fact check on each story, making 16 fact checks.

Side note: All of this python code is running on Mac and Linux.

## About Fact-Check Scoring
The AI fact-check tool returns a number between +2 and -2, the average of evaluating ever statement in a single report. The scores are tallied statement by statement, 2 points for True, 1 for Mostly_true,
0 points for Opinion (does not count in the average), -1 for Mostly_false, and -2 for False. We don't want Opinion statements to dilute the scoring, however the number and ratio of Opinion to the other statements is additional information worth using. The sheer number of statements is also of interest.

## A Cross-Product Table
Producing a Cross-Product Table is quite useful. Across the main diagonal is the condition where the AI that wrote the story is also fact-checking the story. In theory, how can an AI fact-checker not give itself 100% true?  A point worth exploring.

Exploring the average of the rows and columns gives you information about how multiple AI write an story and fact-check a story.

Looking at the Story x Fact-Check matrix, numbers pop out. What can someone read from a cross-product table for numbers that stand out?

In addition to a simple 2D table, are there additional visualizations that can be generated in Python that expose more insights as to what is happening in the data?

## Garbage-In Garbage-Out
What AI prompts are useful to produce the most meaningful story for an experiment such as the Cross-Product? What AI prompts should be used to perform a Fact-Check?

For the data provided, after headers, titles and obvious non-statements are omitted, basically paragraphs are presented to the AI one statement at a time with instruction how to fact check it, also to break it up into parts if it represents multiple statements. A typical 1200 word story appears to be around 60 statements, it is up to the AI to decide. Another study I suppose.

## A Set Of Questions and Requests
1. What can be learned from the data provided?
2. How can the data provided be visualized to expose interesting findings?
3. What makes a good prompt for AI to write a story?
4. What makes a good prompt for AI to Cross-Check a story?
5. Can you write some python to visualize the Cross-Product data?

The following data is in a JSON object. Why python code do I need for visualization and analysis?

STORY
  S  Make        Model                       Title
  1  openai      gpt-4o                      The Rise of Electric Vehicles: Transforming the Automotive I
  2  xai         grok-2-latest               The Unseen Impact of Community Gardens: A Story of Growth an
  3  perplexity  sonar                       The Unyielding Legacy of Stephen Hawking: A Story of Triumph
  4  anthropic   claude-3-7-sonnet-20250219  Rising Temperatures: The Global Reality of Climate Change

FACT CHECK
  S    F  Make        Model                         True    Mostly    Opinion    Mostly    False    Score
                                                              True                False
  1    1  xai         grok-2-latest                   36         9         23         0        0     1.8
  1    2  openai      gpt-4o                          26         9          9         0        0     1.74
  1    3  perplexity  sonar                           33         7          5         0        0     1.82
  1    4  anthropic   claude-3-7-sonnet-20250219      42        13          4         0        0     1.76
  2    1  xai         grok-2-latest                   18         5         15         0        0     1.78
  2    2  anthropic   claude-3-7-sonnet-20250219      19         9          2         1        1     1.47
  2    3  openai      gpt-4o                          11         8         10         0        0     1.58
  2    4  perplexity  sonar                           10         7         11         5        1     0.87
  3    1  xai         grok-2-latest                   36         5         13         0        0     1.88
  3    2  anthropic   claude-3-7-sonnet-20250219      28         4          4         2        0     1.71
  3    3  openai      gpt-4o                          17         7          7         0        0     1.71
  3    4  perplexity  sonar                           25         3          6         0        0     1.89
  4    1  xai         grok-2-latest                   38        10          6         1        1     1.66
  4    2  anthropic   claude-3-7-sonnet-20250219      44         3          1         0        0     1.94
  4    3  openai      gpt-4o                          25         6          2         0        1     1.69
  4    4  perplexity  sonar                           22         9          5         8        1     1.07


# Cross Product of AI Story and Fact Check

1. Use each AI to generate a story with the same prompt
```
story_a = story(ai_a, prompt)
story_b = story(ai_b, prompt)
story_c = story(ai_c, prompt)
```
2. Use each AI to fact check each story
```
aa = fact_check(ai_a, story_a)
ab = fact_check(ai_a, story_b)
ac = fact_check(ai_a, story_c)
ba = fact_check(ai_b, story_a)
bb = fact_check(ai_b, story_b)
bc = fact_check(ai_b, story_c)
ca = fact_check(ai_c, story_a)
cb = fact_check(ai_c, story_b)
cc = fact_check(ai_c, story_c)
```
fact_check returns a number between +2 and -2, the average of evaluating 
a story point by point, 2 points for true, 1 for mostly true, 
0 for opinion (does not count in the average)
-1 for mostly false, and -2 for false
3. Present the result of a cross product of AI on AI
results:
```
aa, ab, ac
ba, bb, bc
ca, cb, cc
```

# The "Cross Product" of AI Story and Fact Check

Imagine you’re running an experiment with three AIs—let’s call them `AI_a`, `AI_b`, and `AI_c`. You give each one the same prompt to generate a story, producing three distinct outputs: `story_a`, `story_b`, and `story_c`. Then, you turn these AIs into fact-checkers, asking each to evaluate all three stories (including its own) on a point-by-point basis, assigning scores from `-2` (false) to `+2` (true). The result is a matrix of scores that reveals how each AI "sees" the truthfulness of every story. This setup is dubbed a "cross product" because it systematically crosses every AI’s storytelling with every AI’s fact-checking, much like how a vector cross product pairs components of two vectors.

## Step-by-Step Breakdown

1. **Story Generation**  
   Each AI takes the same prompt and spins its own tale:  
   - `story_a = story(ai_a, prompt)`  
   - `story_b = story(ai_b, prompt)`  
   - `story_c = story(ai_c, prompt)`  
   Think of these stories as "vectors" of narrative content, each with its own direction (style, details, etc.).

2. **Fact-Checking Phase**  
   Now, each AI evaluates every story, including its own, breaking them down into individual points and scoring them:  
   - `+2`: True (fully factual)  
   - `+1`: Mostly true  
   - `0`: Opinion (excluded from the average)  
   - `-1`: Mostly false  
   - `-2`: False  
   The fact-check score for a story is the average of these point-by-point evaluations. This produces a 3×3 grid of results:  
   - AI_a checks all stories: 
     - `aa = fact_check(ai_a, story_a)`, 
     - `ab = fact_check(ai_a, story_b)`, 
     - `ac = fact_check(ai_a, story_c)`  
   - AI_b checks all stories: `ba`, `bb`, `bc`  
   - AI_c checks all stories: `ca`, `cb`, `cc`

3. **The "Cross Product" Result**  
   The outcome is presented as a matrix:  
```
   aa, ab, ac
   ba, bb, bc
   ca, cb, cc
```
Each entry (e.g., `ab`) is a scalar value between `-2` and `+2`, representing one AI’s judgment of an-other's story. This matrix isn’t a vector like in the mathematical cross product, but it captures a "crossed" interaction—every AI’s perspective on every story, forming a comparative landscape of truthfulness.

## What It Means

This "cross product" isn’t about perpendicularity or areas (as in vector math) but about systematically pairing and evaluating two sets of capabilities: storytelling and fact-checking. It’s a way to explore consistency, bias, or divergence among AIs. For instance:  
- If `aa`, `bb`, and `cc` (self-checks) are high, each AI might be overly generous with its own work.  
- If `ab` and `ba` differ sharply, `AI_a` and `AI_b` might have conflicting notions of truth.  
- A row like `aa, ab, ac` shows how `AI_a` judges all stories, while a column like `aa, ba, ca` shows how `story_a` fares across all AIs.

## Why It’s Cool

It’s a playful twist on the cross product idea, re-purposing it to map out an AI "truth space." You could analyze this matrix to spot patterns—like which AI is the harshest critic or which story holds up best across evaluators. It’s less about geometry and more about a structured clash of perspectives.


## Cross product analysis
I have use 4 different AI to process a prompt generating 4 stories.
Next use the same 4 AI, to fact-check each story, making 16 fact check.
A fact-check is scored based on a scale between +2 and -2, 
the average of evaluating  a story point by point, 
2 points for true, 
1 for mostly true, 
0 for opinion (does not count in the average)
-1 for mostly false, and 
-2 for false
What does this tell us? Is there AI bias? You would think the AI evaluating it's own story would be 100% true. 
Is it possible to be good at story telling but bad at fact-checking?
Your insights are appreciated.

Here are the results. 
STORY
  S  Make        Model                       Title
  1  xai         grok-2-latest               Breakfast Diets: A Comparative Analysis of Energy Levels and
  2  anthropic   claude-3-7-sonnet-20250219  Energy Dynamics: Comparing Three Breakfast Options for Susta
  3  openai      gpt-4o                      Morning Fuel: A Comparative Analysis of Three Breakfast Diet
  4  perplexity  sonar                       The Breakfast Dilemma: A Comparative Analysis of Three Morni

FACT CHECK
  S    F  Make        Model                         True    Mostly    Opinion    Mostly    False    Score
                                                              True                False
  1    1  xai         grok-2-latest                    3        38         25         0        0     1.07
  1    2  anthropic   claude-3-7-sonnet-20250219       9        17         12         2        3     0.87
  1    3  openai      gpt-4o                           4        22         10         4        0     0.87
  1    4  perplexity  sonar                           11        22         13         1        0     1.26
  2    1  xai         grok-2-latest                   13        27         16         1        0     1.27
  2    2  anthropic   claude-3-7-sonnet-20250219      19        16          1         2        0     1.41
  2    3  openai      gpt-4o                          11        26          9         1        0     1.24
  2    4  perplexity  sonar                           20        16         13         5        0     1.24
  3    1  xai         grok-2-latest                   18        19         18         0        0     1.49
  3    2  anthropic   claude-3-7-sonnet-20250219      21        17          3         0        0     1.55
  3    3  openai      gpt-4o                          12        14          9         0        0     1.46
  3    4  perplexity  sonar                           21        11          9         1        1     1.47
  4    1  xai         grok-2-latest                   13        19         24         0        1     1.3
  4    2  anthropic   claude-3-7-sonnet-20250219      18        18          6         2        4     1.05
  4    3  openai      gpt-4o                          10        23         12         3        1     1.03
  4    4  perplexity  sonar                           13        17         15         6        0     1.03
