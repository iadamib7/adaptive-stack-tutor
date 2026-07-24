from backend.app.learning.question_bank.question import DifficultyLevel


def mastery_to_difficulty(mastery_score: float) -> DifficultyLevel:
    """
    Convert a mastery score between 0.0 and 1.0 into a question difficulty.
    """

    if mastery_score < 0.30:
        return DifficultyLevel.BEGINNER

    if mastery_score < 0.50:
        return DifficultyLevel.EASY

    if mastery_score < 0.70:
        return DifficultyLevel.INTERMEDIATE

    if mastery_score < 0.90:
        return DifficultyLevel.ADVANCED

    return DifficultyLevel.EXPERT