"""Тесты локализации, уровней и пользовательского прогресса."""

import unittest

from localization import (
    DEFAULT_LANGUAGE,
    TRANSLATIONS,
    calculate_level,
    make_progress_bar,
    normalize_language,
    t,
)


class LanguageTests(unittest.TestCase):
    """Проверяет выбор языка и целостность переводов."""

    def test_supported_languages_are_preserved(self) -> None:
        """Поддерживаемые языки не должны заменяться языком по умолчанию."""
        self.assertEqual(normalize_language("ru"), "ru")
        self.assertEqual(normalize_language("en"), "en")

    def test_unknown_language_uses_default(self) -> None:
        """Неизвестный или отсутствующий язык должен заменяться русским."""
        self.assertEqual(normalize_language("de"), DEFAULT_LANGUAGE)
        self.assertEqual(normalize_language(None), DEFAULT_LANGUAGE)

    def test_translation_keys_match(self) -> None:
        """Русский и английский словари должны содержать одинаковые ключи."""
        self.assertEqual(
            set(TRANSLATIONS["ru"]),
            set(TRANSLATIONS["en"]),
        )

    def test_unknown_translation_key_is_returned_as_text(self) -> None:
        """Неизвестный ключ должен возвращаться без ошибки."""
        self.assertEqual(
            t("en", "missing_translation_key"),
            "missing_translation_key",
        )


class LevelTests(unittest.TestCase):
    """Проверяет расчёт уровней и накопленного опыта."""

    def test_initial_level(self) -> None:
        """Пользователь без опыта должен находиться на первом уровне."""
        level = calculate_level(0, "en")

        self.assertEqual(level["level"], 1)
        self.assertEqual(level["xp_current"], 0)
        self.assertEqual(level["xp_for_next"], 50)
        self.assertEqual(level["title"], "Beginner")

    def test_level_increases_at_threshold(self) -> None:
        """После получения 50 XP пользователь должен перейти на второй уровень."""
        level = calculate_level(50, "en")

        self.assertEqual(level["level"], 2)
        self.assertEqual(level["xp_current"], 0)
        self.assertEqual(level["xp_for_next"], 100)
        self.assertEqual(level["title"], "Helper")

    def test_experience_is_carried_to_next_level(self) -> None:
        """Опыт сверх порога должен сохраняться на новом уровне."""
        level = calculate_level(75, "en")

        self.assertEqual(level["level"], 2)
        self.assertEqual(level["xp_current"], 25)

    def test_negative_experience_is_treated_as_zero(self) -> None:
        """Отрицательное количество опыта не должно ломать расчёт."""
        level = calculate_level(-100, "en")

        self.assertEqual(level["level"], 1)
        self.assertEqual(level["xp_current"], 0)


class ProgressBarTests(unittest.TestCase):
    """Проверяет формирование текстового прогресс-бара."""

    def test_partial_progress(self) -> None:
        """Прогресс-бар должен показывать процент заполнения."""
        self.assertEqual(
            make_progress_bar(25, 100),
            "🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜ 25%",
        )

    def test_progress_is_limited_to_one_hundred_percent(self) -> None:
        """Значение выше максимума должно ограничиваться ста процентами."""
        self.assertEqual(
            make_progress_bar(150, 100),
            "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%",
        )

    def test_zero_total_is_complete(self) -> None:
        """Нулевое требование должно считаться выполненным."""
        self.assertEqual(
            make_progress_bar(0, 0),
            "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%",
        )


if __name__ == "__main__":
    unittest.main()