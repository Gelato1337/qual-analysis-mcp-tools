# Study brief: the 17 expert interviews

`intent.yaml` is the study brief for re-analysing the 17 expert interviews behind:

- Laato, S., Mäntymäki, M., Islam, A. K. M. N., Hyrynsalmi, S., & Birkstedt, T. (2023). Trends and
  Trajectories in the Software Industry: implications for the future of work. *Information Systems
  Frontiers*, 25(2), 929–944. https://doi.org/10.1007/s10796-022-10267-4 (open access, CC BY 4.0)
- Laato, J., Mäntymäki, M., Kordyaka, B., & Laato, S. (2025). Automating Qualitative Data Analysis
  with Chain-of-Thought Reasoning Models: A Study with the Gioia Method. AMCIS 2025.

## Where each field comes from

| Field | Source in the 2023 paper |
|---|---|
| research_question | RQ1 and RQ2, verbatim (Introduction) |
| stance | Methodology (expert interview study, macro-level view, Finnish informants) |
| prior_research | Background 2.1 (digital transformation, changing nature of work, trend identification) |
| sensitizing_concepts | Background 2.2 (cultural lag theory); the order of use follows 3.2 (lens added in the third analysis stage) |
| study_context | 3.1 (sampling, informants, interviews), Appendix A (protocol), transcript headers (notation), and the earlier `context/study_context.md` (unit of coding, lifecycle models) |

## Kept out on purpose

Nothing from the paper's results reaches the agent: no 1st-order concepts (Table 2), no themes or
dimensions (Fig. 1, Section 4, Table 3), no discussion, no citation of the paper itself. The prior
research names no specific technologies, although the paper's background does (ML, cloud, DevOps,
low code ...): listing them would prime the 1st-order coding. Priming with them is a study parameter
for later, not the default.

Do not add examples from the published analysis to any brief or guide. The earlier
`context/study_context.md` contained one (a published 1st-order concept) and was removed.

## Before running

The paper is open access and was probably in the model's training data. Run the contamination probe
(`probe.md`) before any analysis and keep its answer with the run.
