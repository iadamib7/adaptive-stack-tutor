from backend.app.content.ingestion.concept_mapping_rules import (
    ConceptMappingRule,
)


NUMBAS_TRANSITION_MAPPING_RULES = [
    ConceptMappingRule(
        rule_id="numbas-mean-median-mode",
        concept_id="statistics",
        title_contains=(
            "mean",
            "median",
            "mode",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-die-probability",
        concept_id="probability",
        title_contains=(
            "probability",
            "die",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-pythagoras-side-length",
        concept_id="pythagorean-theorem",
        title_contains=(
            "pythagoras",
            "calculating side length",
        ),
    ),

    ConceptMappingRule(
    rule_id="numbas-pythagoras-general",
    concept_id="pythagorean-theorem",
    title_contains=(
        "pythagoras",
    ),
),

    ConceptMappingRule(
        rule_id="numbas-order-of-operations",
        concept_id="order-of-operations",
        title_contains=(
            "calculate an expression",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-basic-linear-equations",
        concept_id="linear-equations",
        title_contains=(
            "solving linear equations",
        ),
    ),

    ConceptMappingRule(
    rule_id="numbas-linear-equations-general",
    concept_id="linear-equations",
    title_contains=(
        "linear equations",
    ),
),

    # Highly specific real transition questions first.

    ConceptMappingRule(
        rule_id="numbas-decimals-to-fractions",
        concept_id="decimals",
        category_contains=(
            "decimals",
            "fractions",
        ),
        title_contains=(
            "decimals to fractions",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-add-subtract-fractions",
        concept_id="fractions",
        category_contains=(
            "fractions",
        ),
        title_contains=(
            "addition and subtraction of fractions",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-expand-collect",
        concept_id="algebraic-expressions",
        category_contains=(
            "simplifying algebraic expressions",
        ),
        title_contains=(
            "expand brackets",
            "collect like terms",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-student-discount",
        concept_id="percentages",
        category_contains=(
            "percentages",
        ),
        title_contains=(
            "student discount",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-square-cube",
        concept_id="indices",
        category_contains=(
            "indices",
            "powers",
        ),
        title_contains=(
            "square and cube numbers",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-sequence-difference",
        concept_id="arithmetic-sequences",
        category_contains=(
            "sequences",
            "common difference",
        ),
        title_contains=(
            "arithmetic sequences",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-sequence-formula",
        concept_id="arithmetic-sequences",
        category_contains=(
            "sequences",
            "nth term",
        ),
        title_contains=(
            "arithmetic sequence",
        ),
    ),

    # General fallback rules.

    ConceptMappingRule(
        rule_id="numbas-fractions",
        concept_id="fractions",
        category_contains=(
            "fractions",
        ),
        title_contains=(
            "fractions",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-decimals",
        concept_id="decimals",
        category_contains=(
            "decimals",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-percentages",
        concept_id="percentages",
        category_contains=(
            "percentages",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-probability",
        concept_id="probability",
        category_contains=(
            "probability",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-surds",
        concept_id="roots-and-surds",
        category_contains=(
            "surds",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-indices",
        concept_id="indices",
        category_contains=(
            "indices",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-algebraic-expressions",
        concept_id="algebraic-expressions",
        category_contains=(
            "algebraic expressions",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-arithmetic-sequences",
        concept_id="arithmetic-sequences",
        category_contains=(
            "arithmetic sequences",
        ),
    ),

    # Ratio and proportion.
    # Separate rules are intentional because title_contains
    # conditions are combined rather than treated as OR.

    ConceptMappingRule(
        rule_id="numbas-ratio",
        concept_id="ratio-and-proportion",
        title_contains=(
            "ratio",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-proportional-reasoning",
        concept_id="ratio-and-proportion",
        title_contains=(
            "proportion",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-factorisation",
        concept_id="factorisation",
        title_contains=(
            "factoris",
        ),
    ),

    ConceptMappingRule(
    rule_id="numbas-linear-inequalities",
    concept_id="inequalities",
    title_contains=(
        "solving linear inequalities",
    ),
),
    ConceptMappingRule(
    rule_id="numbas-simultaneous-equations",
    concept_id="simultaneous-equations",
    title_contains=(
        "simultaneous",
        "linear equations",
    ),
),

       ConceptMappingRule(
    rule_id="numbas-angles-in-triangles",
    concept_id="angles",
    title_contains=(
        "ga01",
        "angles in triangles",
    ),
),

    ConceptMappingRule(
    rule_id="numbas-angles-of-polygon",
    concept_id="geometry",
    title_contains=(
        "angles of a polygon",
    ),
),

    ConceptMappingRule(
        rule_id="numbas-missing-angle",
        concept_id="angles",
        title_contains=(
            "missing angle",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-angle-relationships",
        concept_id="angles",
        title_contains=(
            "angle relationships",
        ),
    ),

    ConceptMappingRule(
        rule_id="numbas-triangle-properties",
        concept_id="triangles",
        title_contains=(
            "triangles",
        ),
    ),

    ConceptMappingRule(
    rule_id="numbas-number-sense-place-value",
    concept_id="number-sense",
    title_contains=(
        "face, place and actual value",
    ),
),

ConceptMappingRule(
    rule_id="numbas-linear-graph-coordinates",
    concept_id="coordinate-graphs",
    title_contains=(
        "linear",
        "coordinates",
    ),
),

ConceptMappingRule(
    rule_id="numbas-gradient-straight-line",
    concept_id="gradient",
    title_contains=(
        "gradient",
        "straight line",
    ),
),

ConceptMappingRule(
    rule_id="numbas-surds-title",
    concept_id="roots-and-surds",
    title_contains=(
        "surds",
    ),
),

ConceptMappingRule(
    rule_id="numbas-quadratic-polynomial-expand",
    concept_id="quadratic-expressions",
    title_contains=(
        "polynomials",
        "expand and simplify",
    ),
),

ConceptMappingRule(
    rule_id="numbas-bidmas",
    concept_id="order-of-operations",
    title_contains=(
        "bidmas",
    ),
),

ConceptMappingRule(
    rule_id="numbas-negative-number-addition",
    concept_id="integer-operations",
    title_contains=(
        "adding negative numbers",
    ),
),

ConceptMappingRule(
    rule_id="numbas-right-angle-trigonometry",
    concept_id="trigonometry",
    title_contains=(
        "right angle trigonometry",
    ),
),

ConceptMappingRule(
    rule_id="numbas-matrix-arithmetics",
    concept_id="matrices",
    title_contains=(
        "matrix arithmetics",
    ),
),

ConceptMappingRule(
    rule_id="numbas-rectangle-area-perimeter",
    concept_id="mensuration",
    title_contains=(
        "rectangle area and perimeter",
    ),
),

ConceptMappingRule(
    rule_id="numbas-cuboid-surface-area-volume",
    concept_id="surface-area-and-volume",
    title_contains=(
        "volume and surface area of cuboids",
    ),
),

ConceptMappingRule(
    rule_id="numbas-enlargement-scale-factor",
    concept_id="similarity",
    title_contains=(
        "transformation",
        "enlargement",
    ),
),
]
