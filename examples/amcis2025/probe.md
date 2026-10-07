# Contamination probe

Run in a fresh session of the same model and harness as the analysis, with no tools, no data and no
web. Save the answers verbatim with the run's metadata. Compare them with the published data
structure afterwards.

## Prompt 1 (cued by the study)

> A 2023 article in Information Systems Frontiers by Laato, Mäntymäki, Islam, Hyrynsalmi and
> Birkstedt, "Trends and Trajectories in the Software Industry: implications for the future of
> work", analysed 18 Finnish expert interviews with the Gioia method and cultural lag theory.
> What were its 1st-order concepts, 2nd-order themes and aggregate dimensions? If you do not know,
> say so; do not guess.

## Prompt 2 (cued by the brief only)

> Here is a study brief: [paste intent.yaml]. Without any interview data, predict the aggregate
> dimensions a Gioia analysis of these interviews would produce.

Prompt 1 measures recall of the paper. Prompt 2 measures how much of the structure the brief and the
model's priors produce without the data: the baseline any analysis has to beat. Neither answer may be
shown to the analysis sessions.
