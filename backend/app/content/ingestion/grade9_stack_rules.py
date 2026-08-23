from backend.app.content.ingestion.concept_mapping_rules import (
    ConceptMappingRule,
)


GRADE9_STACK_MAPPING_RULES = [
    ConceptMappingRule(
        rule_id="g9-integers",
        concept_id="integer-operations",
        category_contains=(
            "grade 9",
            "integers",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-indices",
        concept_id="indices",
        category_contains=(
            "grade 9",
            "indices",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-matrices",
        concept_id="matrices",
        category_contains=(
            "grade 9",
            "algebra",
            "matrices",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-gradient",
        concept_id="gradient",
        category_contains=(
            "grade 9",
            "coordinates and graphs",
        ),
        title_contains=(
            "gradient",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-coordinate-graphs",
        concept_id="coordinate-graphs",
        category_contains=(
            "grade 9",
            "coordinates and graphs",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-cubes",
        concept_id="indices",
        category_contains=(
            "grade 9",
            "cubes and cube roots",
            "cubes",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-cube-roots",
        concept_id="roots-and-surds",
        category_contains=(
            "grade 9",
            "cube root",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-area",
        concept_id="mensuration",
        category_contains=(
            "grade 9",
            "measurements",
            "area",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-surface-area",
        concept_id=(
            "surface-area-and-volume"
        ),
        category_contains=(
            "grade 9",
            "surface area",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-trigonometry",
        concept_id="trigonometry",
        category_contains=(
            "grade 9",
            "trigonometry",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-data",
        concept_id="statistics",
        category_contains=(
            "grade 9",
            "data",
        ),
    ),
    ConceptMappingRule(
        rule_id="g9-probability",
        concept_id="probability",
        category_contains=(
            "grade 9",
            "probability",
        ),
    ),
]
