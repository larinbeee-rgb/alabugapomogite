import unittest
import os
import tempfile
import tkinter as tk
from weather_diary import WeatherDiary

class TestWeatherDiary(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        import weather_diary
        self.original_data_file = weather_diary.DATA_FILE
        weather_diary.DATA_FILE = os.path.join(self.temp_dir.name, "test.json")
        self.root = tk.Tk()
        self.app = WeatherDiary(self.root)

    def tearDown(self):
        self.root.destroy()
        self.temp_dir.cleanup()
        import weather_diary
        weather_diary.DATA_FILE = self.original_data_file

    def test_validate_date_valid(self):
        result = self.app.validate_date("2025-05-04")
        self.assertTrue(result)

    def test_validate_date_invalid_format(self):
        result = self.app.validate_date("04.05.2025")
        self.assertFalse(result)

    def test_validate_date_wrong_month(self):
        result = self.app.validate_date("2025-13-01")
        self.assertFalse(result)

    def test_validate_temperature_valid(self):
        result = self.app.validate_temperature("23.5")
        self.assertEqual(result, 23.5)

    def test_validate_temperature_negative(self):
        result = self.app.validate_temperature("-15")
        self.assertEqual(result, -15)

    def test_validate_temperature_too_cold(self):
        result = self.app.validate_temperature("-100")
        self.assertIsNone(result)

    def test_validate_temperature_too_hot(self):
        result = self.app.validate_temperature("70")
        self.assertIsNone(result)

    def test_validate_temperature_not_number(self):
        result = self.app.validate_temperature("жарко")
        self.assertIsNone(result)

    def test_add_record_success(self):
        self.app.date_var.set("2025-05-04")
        self.app.temp_var.set("22")
        self.app.description_var.set("Солнечно")
        self.app.precipitation_var.set("Нет")
        self.app.add_record()
        self.assertEqual(len(self.app.records), 1)
        self.assertEqual(self.app.records[0]["description"], "Солнечно")

    def test_filter_by_date(self):
        self.app.records = [
            {"id": 1, "date": "2025-05-01", "temperature": 20, "description": "A", "precipitation": "Нет"},
            {"id": 2, "date": "2025-05-02", "temperature": 22, "description": "B", "precipitation": "Дождь"}
        ]
        self.app.refresh_table()
        self.app.filter_date_var.set("2025-05-02")
        self.app.apply_filter()
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)

    def test_filter_by_temperature_above(self):
        self.app.records = [
            {"id": 1, "date": "2025-05-01", "temperature": 10, "description": "A", "precipitation": "Нет"},
            {"id": 2, "date": "2025-05-02", "temperature": 20, "description": "B", "precipitation": "Дождь"}
        ]
        self.app.refresh_table()
        self.app.filter_temp_var.set("15")
        self.app.filter_temp_operator.set(">")
        self.app.apply_filter()
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)

    def test_filter_by_temperature_below(self):
        self.app.records = [
            {"id": 1, "date": "2025-05-01", "temperature": 5, "description": "A", "precipitation": "Нет"},
            {"id": 2, "date": "2025-05-02", "temperature": 20, "description": "B", "precipitation": "Дождь"}
        ]
        self.app.refresh_table()
        self.app.filter_temp_var.set("10")
        self.app.filter_temp_operator.set("<")
        self.app.apply_filter()
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)

    def test_stats_calculation(self):
        self.app.records = [
            {"id": 1, "date": "2025-01-01", "temperature": 25, "description": "A", "precipitation": "Нет"},
            {"id": 2, "date": "2025-01-02", "temperature": 15, "description": "B", "precipitation": "Дождь"}
        ]
        avg_temp = sum(r["temperature"] for r in self.app.records) / len(self.app.records)
        self.assertEqual(avg_temp, 20)

if __name__ == "__main__":
    unittest.main()