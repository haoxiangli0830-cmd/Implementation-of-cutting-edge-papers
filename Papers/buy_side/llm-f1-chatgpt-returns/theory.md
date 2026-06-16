# theory (light) — News sentiment → returns

Deep dives → 74-week curriculum (ML-for-risk: NLP, classification).

## The idea
News moves prices. If a model can read a headline and judge "good or bad for this
company," and if the market hasn't fully priced it in yet, that judgment should
predict the next move. The paper's twist: modern **language models** read the
headline far better than old keyword/lexicon methods.

## Sentiment, three ways (cheapest → priciest)
1. **Lexicon** (count positive/negative words) — crude, misses context/negation.
2. **FinBERT** (what we use) — a BERT model fine-tuned on financial text; reads
   context, free and local. Our benchmark: **84% directional accuracy**.
3. **Large LLM** (ChatGPT/Claude) — best reasoning, but costs money/API access.

## The pipeline (identical for any engine)
headline → sentiment score (−1…+1) → average per stock per day → rank stocks →
long the most positive, short the most negative → measure next-day return.

## The honesty issues to watch
- **Timing/look-ahead:** only trade on news *timestamped before* the return window.
  A headline at 3pm can't be used to "predict" that day's open.
- **It's mostly a *short-horizon* effect:** sentiment predicts the next day or two,
  then decays — so transaction costs matter a lot. The rigor layer (costs +
  Deflated Sharpe) is essential before believing any Sharpe here.
