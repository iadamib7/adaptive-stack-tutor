import pytest

from backend.app.learning.adaptive_engine import (
    StackXmlQuestionBankImporter,
)

from backend.app.learning.adaptive_engine.metadata import (
    AdaptiveMetadataLoader,
)


XML = """
<quiz>
  <question type="stack">
    <name>
      <text>Entry diagnostic</text>
    </name>
    <idnumber>Q1</idnumber>
    <questiontext format="html">
      <text>Entry</text>
    </questiontext>
  </question>

  <question type="stack">
    <name>
      <text>Targeted support</text>
    </name>
    <idnumber>Q2</idnumber>
    <questiontext format="html">
      <text>Support</text>
    </questiontext>
  </question>
</quiz>
"""


METADATA = """
{
  "questions": {
    "Q1": {
      "difficulty": 0.0,
      "tags": [
        "diagnostic"
      ],
      "prt_outcomes": {
        "prt1:prt1-1-F|prt1-2-T":
          "sign_error"
      }
    },
    "Q2": {
      "difficulty": -0.4,
      "supports": [
        "sign_error"
      ]
    }
  }
}
"""


def build_bank():
    importer = (
        StackXmlQuestionBankImporter()
    )

    return importer.import_text(
        XML
    )


def test_metadata_applies_difficulty() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        METADATA
    )

    bank = loader.apply(
        bank=build_bank(),
        manifest=manifest,
    )

    q2 = bank.require(
        "Q2"
    ).adaptive_question

    assert q2.difficulty == -0.4


def test_metadata_applies_support_tags() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        METADATA
    )

    bank = loader.apply(
        bank=build_bank(),
        manifest=manifest,
    )

    q2 = bank.require(
        "Q2"
    ).adaptive_question

    assert q2.supports == (
        "sign_error",
    )


def test_metadata_applies_general_tags() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        METADATA
    )

    bank = loader.apply(
        bank=build_bank(),
        manifest=manifest,
    )

    q1 = bank.require(
        "Q1"
    ).adaptive_question

    assert q1.tags == (
        "diagnostic",
    )


def test_manifest_exposes_prt_aliases() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        METADATA
    )

    aliases = (
        manifest.outcome_aliases()
    )

    assert aliases["Q1"][
        "prt1:prt1-1-F|prt1-2-T"
    ] == "sign_error"


def test_metadata_does_not_require_curriculum() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        METADATA
    )

    assert not hasattr(
        manifest,
        "curriculum"
    )

    assert not hasattr(
        manifest,
        "standard"
    )

    assert not hasattr(
        manifest,
        "concept_id"
    )


def test_unknown_question_is_rejected() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        """
        {
          "questions": {
            "DOES_NOT_EXIST": {
              "difficulty": 0.5
            }
          }
        }
        """
    )

    with pytest.raises(
        ValueError,
    ):
        loader.apply(
            bank=build_bank(),
            manifest=manifest,
        )


def test_invalid_difficulty_is_rejected() -> None:
    loader = AdaptiveMetadataLoader()

    with pytest.raises(
        ValueError,
    ):
        loader.load_text(
            """
            {
              "questions": {
                "Q1": {
                  "difficulty": 99
                }
              }
            }
            """
        )


def test_empty_metadata_is_allowed() -> None:
    loader = AdaptiveMetadataLoader()

    manifest = loader.load_text(
        """
        {
          "questions": {}
        }
        """
    )

    bank = loader.apply(
        bank=build_bank(),
        manifest=manifest,
    )

    assert bank.count == 2
