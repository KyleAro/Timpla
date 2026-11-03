# Software Development and Evaluation Methodology

## Development Methodology

Timpla is developed using Agile software development. Agile is suitable for this system because ingredient recognition, recipe feasibility, culinary rules, zero-waste suggestions, and the mobile experience depend on one another and require repeated refinement. The work is organized into functional iterations. Each iteration produces a reviewable system increment, and feedback and evaluation findings inform subsequent refinement.

| Iteration | Activities | Deliverables |
| --- | --- | --- |
| 1. Requirements and system design | Define the target users, zero-waste objective, supported ingredients, dietary and allergy constraints, intended-serving input, and the input–process–output flow. Establish acceptance criteria and the product backlog. | Requirements specification, system flow, acceptance criteria, and prioritized backlog |
| 2. Recipe and culinary knowledge preparation | Collect and document Filipino recipe sources; clean and deduplicate recipe records; normalize ingredient names while preserving the original ingredient wording; identify essential, supporting, and optional roles; document approved substitutions and safety constraints. | Versioned Filipino recipe collection, ingredient ontology, provenance records, and reviewed culinary rules |
| 3. Ingredient-recognition preparation | Collect and annotate ingredient images; define training, validation, and test partitions; train and compare object-detection configurations; record experiment settings and evaluate on held-out images. | Versioned image dataset and annotation manifest, trained detector artifact, and experiment and evaluation records |
| 4. Mobile application development | Implement image capture and upload, detector communication, result display, manual correction of recognized ingredients, and entry of serving, allergy, diet, and other relevant preferences. | Mobile application supporting the ingredient-input and confirmation flow |
| 5. Recommendation development | Compare confirmed inventory with reviewed recipe requirements; identify feasible source recipes and disclose missing supporting items; rank eligible recipes; provide a separately identified food-utilization suggestion when an exact source recipe does not fit the inventory. | Integrated recommendation component with feasibility decisions, ranked results, ingredient explanations, and zero-waste suggestions |
| 6. System evaluation and refinement | Evaluate recognition, recipe feasibility and ranking, culinary knowledge quality, and user-centered performance; correct defects identified during evaluation; record limitations and prepare technical and research documentation. | Evaluated research prototype, evaluation records, corrected release, and technical documentation |

## System Flow

The system accepts an ingredient image captured or uploaded by the user, or ingredients entered manually. The user may provide intended servings and relevant dietary restrictions, allergies, exclusions, or ingredients to use first. Ingredient recognition proposes labels from the image, and the user confirms or corrects them before recommendation. The confirmed inventory is compared with a Filipino recipe database and its ingredient ontology and reviewed culinary rules. The system presents ranked feasible dishes, indicates which ingredients are available and which supporting items need confirmation, and may provide a clearly identified food-utilization suggestion. Dietary and allergy constraints are applied as restrictions, and explanations and safety reminders accompany recommendations where applicable.

## Recipe Recommendation and Feasibility Evaluation

### Recommendation objective

Recipe recommendation is evaluated according to Timpla's zero-waste objective: help users identify food they can prepare from ingredients they already have, while making uncertainty and necessary preparation checks clear. A recommendation is not considered suitable merely because its title matches an ingredient or because it has a high ranking score. Feasibility constraints are applied before ranking.

### Recipe and inventory representation

Each recipe record retains its source wording and provenance. Ingredient lines are also mapped, where supported by reviewed evidence, to canonical ingredient identities so that variations in quantities, spelling, preparation, and wording can be compared with the user's confirmed inventory. Normalization identifies ingredient identity; it does not imply that distinct ingredients, forms, or culinary uses are interchangeable.

Reviewed recipes classify ingredients as:

- **Essential:** required for the source recipe's identity or basic preparation.
- **Supporting:** included in the source recipe and relevant to flavor or preparation, but not essential to its core identity.
- **Optional:** explicitly described as optional by the recipe source or reviewed culinary record.

The user's inventory contains confirmed ingredients, including user corrections to detector output. Intended servings, use-first ingredients, exclusions, allergies, and dietary preferences are represented as scenario constraints when supplied. A substitution is allowed only when it appears in the reviewed substitution knowledge base and is compatible with the recipe and user constraints.

### Feasibility and recommendation behavior

The feasibility procedure applies the following rules:

1. A source recipe is eligible as feasible when all of its essential ingredients are confirmed in the inventory or covered by an approved substitution.
2. Allergy, exclusion, and dietary restrictions act as hard constraints. A recipe that conflicts with a supplied restriction is excluded.
3. Supporting and optional ingredients are reported transparently. The system does not silently treat an unconfirmed ingredient as available.
4. Eligible source recipes are ranked only after feasibility checks. Ranking cannot make an ineligible recipe feasible.
5. The system favors useful coverage of ingredients the user wants to use, across the set of recommendations. It does not require every individual recipe to consume every available ingredient.
6. When no source recipe is feasible, the system may offer a separate, clearly labeled food-utilization idea. It must not present a generated or adapted idea as a recipe from the database. Any such idea must use the confirmed inventory and reviewed substitutions, disclose assumptions, and avoid claiming that an unverified combination is a validated recipe.
7. Recommendations identify preparation, quantity, or safety details that cannot be established from ingredient detection alone and require user confirmation.

### Evaluation scenarios and comparison

Evaluation uses inventory scenarios containing confirmed ingredients and, where applicable, serving needs, use-first items, dietary preferences, allergies, and exclusions. Scenarios are separated so that duplicate or near-duplicate inventories do not appear across development and held-out evaluation partitions. The same scenarios and eligibility rules are used when comparing a learned ranking model with a transparent rule-based baseline.

Human relevance judgments use a four-level scale: **0 — unsuitable**, **1 — weak**, **2 — useful**, and **3 — highly useful**. Reviewers judge whether the recommendation is appropriate for the stated inventory and constraints, not whether its title merely resembles an ingredient. When feasible, judgments are collected independently from more than one reviewer and disagreements are resolved using a documented review procedure.

### Measures

| Evaluation aspect | Measure and interpretation |
| --- | --- |
| Feasibility | **Feasibility violation rate:** recommendations that fail an essential-ingredient or user-constraint check divided by all recommendations. A lower rate is better; constraint-conflicting recommendations are expected to be excluded. |
| Ranking quality | **Precision@5:** proportion of the first five recommendations judged useful or highly useful (rating 2 or 3). **NDCG@5:** graded ranking quality using the four-level human relevance judgments. |
| Inventory compliance | **Unconfirmed-ingredient violation rate:** recommendations that assume an ingredient not confirmed in the inventory and not covered by an approved substitution. |
| Zero-waste support | **Use-first coverage:** share of scenarios in which an ingredient explicitly marked to use first is incorporated into at least one suitable recommendation. This is measured across the recommendation set rather than requiring every dish to use every ingredient. |
| Recommendation coverage | **Feasible-result rate:** share of scenarios for which at least one eligible database recipe is returned. Generated or adapted suggestions are reported separately and do not count as database recipes. |
| Knowledge-base quality | Review of ingredient identity mappings, ingredient roles, source provenance, substitutions, and safety constraints for correctness, completeness, and consistency. Reviewer agreement is reported when multiple reviewers participate. |
| User-centered quality | Task completion, ability to identify an option that fits the available ingredients without requiring unlisted purchases, perceived usefulness and clarity, and task completion time. |

Categorical outcomes are summarized using counts and percentages. Precision and NDCG are calculated over the held-out inventory scenarios. Ordinal ratings and completion times are summarized using medians and interquartile ranges, with distributions reported where useful. Results distinguish source-recipe recommendations from food-utilization ideas. Recommendation coverage alone is not interpreted as measured food-waste reduction; demonstrating an actual reduction requires a separate user or household outcome study.

### Ingredient recognition evaluation

Ingredient recognition is evaluated separately from recipe recommendation using held-out annotated images. Evaluation records the dataset partition, class coverage, detector configuration, confidence thresholds, and relevant object-detection measures, including precision, recall, and mAP at the stated IoU threshold. The user-confirmation step is included in the system-level workflow because image recognition may be uncertain and the recommendation stage relies on the corrected inventory. Recognition metrics and recommendation metrics are reported separately; performance in one stage is not treated as evidence of performance in the other.

### Reporting

This methodology specifies the development process, decision rules, evaluation scenarios, and measures. Numerical outcomes, observed defects, and conclusions are reported in the Results and Discussion sections from the corresponding experiment and user-evaluation records.
