import unittest
import json
import io 
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

# Import the class we are testing
from smart_habit import SmartHabit

# --- Mock Data for Testing ---
MOCK_INITIAL_DATA = {
    'habits': [
        {
            "number": 1,
            "name": "Reading",
            "target_hours": 1.0,
            "today_hours": 0.5,
            "completed": False,
            "daily_progress": {"2025-11-20": 0.5},
            "created_date": "2025-11-20"
        },
        {
            "number": 2,
            "name": "Exercise",
            "target_hours": 2.0,
            "today_hours": 2.0,
            "completed": True,
            "daily_progress": {"2025-11-20": 2.0},
            "created_date": "2025-11-20"
        }
    ],
    'next_number': 3,
    'last_updated': "2025-11-20T00:00:00.000000"
}

# Define a specific date object to mock
MOCK_TODAY_DATE = date(2025, 11, 21)
MOCK_TODAY_STR = '2025-11-21'

# --- The Test Suite ---
class TestSmartHabit(unittest.TestCase):
    """
    Test suite for the SmartHabit class, using mocking for file system and time.
    """

    def setUp(self):
        # 1. Mock datetime to freeze time
        mock_datetime_now = MagicMock(spec=datetime)
        # Combine the date with min time to ensure a fixed point in time
        mock_datetime_now.now.return_value = datetime.combine(MOCK_TODAY_DATE, datetime.min.time())

        # patch the standard date object for internal calls to date.today()
        # The datetime module inside smart_habit.py is what needs patching.
        self.mock_datetime_patch = patch('smart_habit.datetime', mock_datetime_now)
        self.mock_datetime = self.mock_datetime_patch.start()
        
        # Ensure date.today() returns the correct mocked date
        self.mock_datetime.date.today.return_value = MOCK_TODAY_DATE
        # Ensure timedelta still works correctly
        self.mock_datetime.timedelta = timedelta

        # 2. Mock file I/O (open) to avoid touching the real file system
        self.mock_open_patch = patch('builtins.open', new_callable=MagicMock)
        self.mock_open = self.mock_open_patch.start()
        
        # Configure the mock open to simulate reading MOCK_INITIAL_DATA
        self.mock_open.return_value.__enter__.return_value = io.StringIO(
            json.dumps(MOCK_INITIAL_DATA)
        )
        
        # Initialize the tracker, which calls load_data() and uses the mocks
        self.tracker = SmartHabit()

    def tearDown(self):
        # Stop all patches after each test to ensure isolation
        self.mock_datetime_patch.stop()
        self.mock_open_patch.stop()

    # --- Core Functionality Tests (load_data, initialization) ---
    
    def test_initial_load_success(self):
        """Test if the tracker loads initial data correctly."""
        self.assertEqual(len(self.tracker.habits), 2)
        self.assertEqual(self.tracker.next_number, 3)
        self.assertEqual(self.tracker.habits[0]['name'], "Reading")
        self.assertEqual(self.tracker.habits[1]['daily_progress'][MOCK_TODAY_STR], 0) # Should be initialized to 0 for today (2025-11-21)

    def test_load_file_not_found(self):
        """Test starting fresh when the data file is missing (FileNotFoundError)."""
        # Stop the current mock open
        self.mock_open_patch.stop()
        
        # Re-patch open to simulate FileNotFoundError
        mock_open_fnf = patch('builtins.open', side_effect=FileNotFoundError)
        mock_open_fnf.start()
        
        # Create a new tracker instance
        new_tracker = SmartHabit()
        
        self.assertEqual(len(new_tracker.habits), 0)
        self.assertEqual(new_tracker.next_number, 1)
        
        # Stop the FNF mock
        mock_open_fnf.stop()

    # --- Habit Management Tests ---
    def test_add_habit(self):
        """Test adding a new habit and checking attributes."""
        
        # Mocking input() for the console version of add_habit
        with patch('builtins.input', side_effect=['Running', '1.5']):
            self.tracker.add_habit()
        
        self.assertEqual(len(self.tracker.habits), 3)
        new_habit = self.tracker.habits[-1]
        
        self.assertEqual(new_habit['name'], 'Running')
        self.assertEqual(new_habit['target_hours'], 1.5)
        self.assertEqual(new_habit['number'], 3) # Should use the next_number
        self.assertIn(MOCK_TODAY_STR, new_habit['daily_progress']) # Check initialization for today
        
        # Check that save_data was called
        self.assertTrue(self.mock_open.called)
        
    def test_find_habit_by_number(self):
        """Test finding an existing habit and handling a non-existent one."""
        habit_1 = self.tracker.find_habit_by_number(1)
        self.assertEqual(habit_1['name'], 'Reading')
        
        habit_99 = self.tracker.find_habit_by_number(99)
        self.assertIsNone(habit_99)

    def test_delete_habit(self):
        """Test deleting a habit."""
        # Mock input for the console version: input habit number (1), input confirmation (yes)
        with patch('builtins.input', side_effect=['1', 'yes']):
            self.tracker.delete_habit()
            
        self.assertEqual(len(self.tracker.habits), 1)
        # Check that 'Reading' (number 1) is gone and 'Exercise' (number 2) remains
        self.assertEqual(self.tracker.habits[0]['number'], 2)
        self.assertTrue(self.mock_open.called)

    # --- Progress and Scoring Tests (Analytics) ---

    def test_calculate_daily_score_correct_ratio(self):
        """
        Test if daily score calculation works with mocked progress for MOCK_TODAY_STR (2025-11-21).
        Habit 1: Reading (1.0h target, 0.5h done) -> Score = 50%
        Habit 2: Exercise (2.0h target, 0.0h done) -> Score = 0%
        Average Score: (50% + 0%) / 2 = 25%
        Completed Habits: 0
        """
        # Manually set progress for the mocked day (2025-11-21)
        self.tracker.habits[0]['daily_progress'][MOCK_TODAY_STR] = 0.5 # Reading (50%)
        self.tracker.habits[1]['daily_progress'][MOCK_TODAY_STR] = 0.0 # Exercise (0%)
        
        score_data = self.tracker.calculate_daily_score()
        
        # Expected daily score is 25.0
        self.assertAlmostEqual(score_data['daily_score'], 25.0)
        # Expected completed habits is 0 (Fixes AssertionError: 0 != 1)
        self.assertEqual(score_data['completed_habits'], 0)
        self.assertEqual(score_data['total_habits'], 2)

    def test_calculate_daily_score_fully_completed(self):
        """Test when all habits are completed."""
        self.tracker.habits[0]['daily_progress'][MOCK_TODAY_STR] = 1.0 # Reading completed
        self.tracker.habits[1]['daily_progress'][MOCK_TODAY_STR] = 2.0 # Exercise completed
        
        score_data = self.tracker.calculate_daily_score()
        
        self.assertAlmostEqual(score_data['daily_score'], 100.0)
        self.assertEqual(score_data['completed_habits'], 2)
        self.assertEqual(score_data['completion_percentage'], 100.0)
    
    def test_calculate_daily_score_zero_habits(self):
        """Test score when there are no habits."""
        self.tracker.habits = []
        score_data = self.tracker.calculate_daily_score()
        
        self.assertEqual(score_data['daily_score'], 0)
        self.assertEqual(score_data['total_habits'], 0)
        self.assertEqual(score_data['completion_percentage'], 0)

    # --- Weekly Progress Test ---
    
    def test_get_weekly_progress(self):
        """
        Test the structure and data aggregation for a full week.
        Data is expected to be ordered [Today, Yesterday, ..., 6 Days Ago]
        """
        habit_num = 1 # Reading
        
        # Date 1 day ago: 2025-11-20
        past_date_1 = (MOCK_TODAY_DATE - timedelta(days=1)).strftime("%Y-%m-%d") 
        # Date 6 days ago: 2025-11-15
        past_date_6 = (MOCK_TODAY_DATE - timedelta(days=6)).strftime("%Y-%m-%d") 
        
        # Set progress for habit 1 (Reading, Target 1.0h)
        # The MOCK_INITIAL_DATA already sets 0.5h for past_date_1 (2025-11-20), but let's change it for test variety
        self.tracker.habits[0]['daily_progress'][past_date_1] = 1.0 # Completed (100%)
        self.tracker.habits[0]['daily_progress'][past_date_6] = 0.5 # Partial (50%)
        # Day 0 (MOCK_TODAY_STR 2025-11-21) is 0.0 (missed)
        
        weekly_progress = self.tracker.get_weekly_progress(habit_num)
        
        self.assertEqual(len(weekly_progress), 7)
        
        # Day 0 - Today (2025-11-21)
        today_data = weekly_progress[0] 
        self.assertEqual(today_data['date'], MOCK_TODAY_STR) # Fixes the date mismatch error
        self.assertFalse(today_data['completed'])
        self.assertEqual(today_data['hours'], 0)
        
        # Day 1 - Yesterday (2025-11-20)
        yesterday_data = weekly_progress[1]
        self.assertEqual(yesterday_data['date'], past_date_1)
        self.assertTrue(yesterday_data['completed'])
        self.assertEqual(yesterday_data['hours'], 1.0)
        self.assertEqual(yesterday_data['completion_percentage'], 100.0)
        
        # Day 6 - 6 Days Ago (2025-11-15)
        day_6_data = weekly_progress[6]
        self.assertEqual(day_6_data['date'], past_date_6)
        self.assertFalse(day_6_data['completed'])
        self.assertEqual(day_6_data['hours'], 0.5)
        self.assertEqual(day_6_data['completion_percentage'], 50.0)

if __name__ == '__main__':
    unittest.main()