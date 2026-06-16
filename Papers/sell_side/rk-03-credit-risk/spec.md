# spec — rk-03-credit-risk

**Domain:** Credit risk (bank risk quant).
**References:** Merton (1974); Vasicek (2002) single-factor model; Basel II/III IRB;
CreditMetrics technical document.

## What a credit-risk desk does
Estimate how likely each borrower is to default (PD), how much is lost if they do
(LGD × EAD), and how much capital the bank must hold against the *whole* portfolio
defaulting more than expected (economic capital / regulatory capital).

## What we implement
1. **Merton structural model**: equity = call option on firm assets → back out
   distance-to-default and PD from equity value, equity vol and debt.
2. **Portfolio model**: Basel single-factor (ASRF). Many obligors share one
   systematic factor; Monte-Carlo the loss distribution → EL, 99.9% Credit VaR,
   economic capital; cross-check vs the Basel IRB analytic capital formula.

## Data
- yfinance equity prices (equity vol) + market cap & total debt from yfinance info.

## Benchmark to reproduce
- DtD/PD order firms by credit quality sensibly (staples safe, levered autos risky).
- Skewed portfolio loss distribution; economic capital ≫ expected loss.
- Concentration: MC capital exceeds the granular IRB figure for a small book.

## Known limits
- Simple Merton (V≈E+D) rather than full KMV iteration; current-snapshot fundamentals.
