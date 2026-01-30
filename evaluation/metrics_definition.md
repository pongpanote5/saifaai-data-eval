# Metrics Definitions

## Cleanliness
Cleanliness estimates how noise-free an extracted output is. It is a heuristic score in `[0.0, 1.0]` that rewards readable, content-focused text and penalizes boilerplate or clutter. The score considers:

- **Character quality**: higher ratios of alphanumeric characters to all characters indicate fewer symbols or markup artifacts.
- **Repetition**: repeated lines suggest navigation, templating, or duplicated boilerplate; more unique lines improve the score.
- **Boilerplate keywords**: occurrences of terms like "cookie", "privacy", "terms", "newsletter", or "accept" reduce the score.
- **Short-line prevalence**: many very short lines can indicate menus or layout noise; too many short lines lower the score.

Cleanliness is **non-gold-standard** and intended only for quick comparisons across pipelines.

## Completeness
Completeness estimates how much meaningful content a candidate output retains **relative to a baseline raw extraction**. It is a heuristic score in `[0.0, 1.0]` and is **not** a ground-truth measure. The score combines:

- **Length ratio**: the ratio of candidate tokens to baseline tokens (saturated at `1.0`).
- **Word coverage**: overlap between the candidate word set and the top-N most frequent baseline words (excluding common stopwords).

Completeness should be used for lightweight, directional evaluation when no labeled reference is available.
