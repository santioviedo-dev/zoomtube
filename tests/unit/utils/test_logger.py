import unittest
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from zoomtube.utils.logger import get_logger, _get_log_dir


class TestGetLogDir(unittest.TestCase):
    """Tests for the _get_log_dir function."""

    @patch('platform.system')
    def test_get_log_dir_windows(self, mock_platform):
        """Test log directory path for Windows."""
        mock_platform.return_value = "Windows"
        with patch.dict('os.environ', {'APPDATA': 'C:\\Users\\TestUser\\AppData\\Roaming'}):
            log_dir = _get_log_dir()
            self.assertIn('zoomtube', str(log_dir))
            self.assertIn('logs', str(log_dir))

    @patch('platform.system')
    def test_get_log_dir_macos(self, mock_platform):
        """Test log directory path for macOS."""
        mock_platform.return_value = "Darwin"
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/Users/testuser')
            log_dir = _get_log_dir()
            self.assertIn('Library', str(log_dir))
            self.assertIn('Logs', str(log_dir))
            self.assertIn('zoomtube', str(log_dir))

    @patch('platform.system')
    def test_get_log_dir_linux(self, mock_platform):
        """Test log directory path for Linux."""
        mock_platform.return_value = "Linux"
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/home/testuser')
            log_dir = _get_log_dir()
            self.assertIn('.local', str(log_dir))
            self.assertIn('share', str(log_dir))
            self.assertIn('zoomtube', str(log_dir))

    @patch('platform.system')
    def test_get_log_dir_creates_directory(self, mock_platform):
        """Test that log directory is created if it doesn't exist."""
        mock_platform.return_value = "Linux"
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                log_dir = _get_log_dir()
                self.assertTrue(log_dir.exists())


class TestGetLogger(unittest.TestCase):
    """Tests for the get_logger function."""

    def setUp(self):
        """Clean up logger handlers before each test."""
        # Clear handlers for any existing loggers to ensure tests are isolated
        for name in list(logging.Logger.manager.loggerDict.keys()):
            try:
                logging.getLogger(name).handlers.clear()
            except Exception:
                # ignore non-logger entries
                pass
        # Also clear handlers on the root logger
        try:
            logging.getLogger().handlers.clear()
        except Exception:
            pass

    def test_get_logger_default(self):
        """Test logger creation with default parameters."""
        logger = get_logger("test_logger_default")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger_default")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_get_logger_has_handlers(self):
        """Test that logger has both console and file handlers."""
        logger = get_logger("test_logger_handlers")
        self.assertGreaterEqual(len(logger.handlers), 2)

    def test_get_logger_console_handler_info_level(self):
        """Test console handler with default (info) level."""
        logger = get_logger("test_logger_info", verbose=False, quiet=False)
        console_handler = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)][0]
        self.assertEqual(console_handler.level, logging.INFO)

    def test_get_logger_console_handler_debug_level(self):
        """Test console handler with verbose=True (debug level)."""
        logger = get_logger("test_logger_verbose", verbose=True)
        console_handler = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)][0]
        self.assertEqual(console_handler.level, logging.DEBUG)

    def test_get_logger_console_handler_error_level(self):
        """Test console handler with quiet=True (error level)."""
        logger = get_logger("test_logger_quiet", quiet=True)
        console_handler = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)][0]
        self.assertEqual(console_handler.level, logging.ERROR)

    def test_get_logger_idempotent(self):
        """Test that calling get_logger twice returns the same logger."""
        logger1 = get_logger("test_logger_idempotent")
        handler_count_1 = len(logger1.handlers)
        logger2 = get_logger("test_logger_idempotent")
        handler_count_2 = len(logger2.handlers)
        self.assertEqual(handler_count_1, handler_count_2)
        self.assertIs(logger1, logger2)

    def test_get_logger_console_formatter(self):
        """Test that console handler has correct formatter."""
        logger = get_logger("test_logger_console_fmt")
        console_handler = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)][0]
        formatter = console_handler.formatter
        self.assertIsNotNone(formatter)
        self.assertIn('levelname', formatter._fmt)

    def test_get_logger_file_handler_exists(self):
        """Test that file handler is created."""
        logger = get_logger("test_logger_file")
        from logging.handlers import RotatingFileHandler
        file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        self.assertEqual(len(file_handlers), 1)

    def test_get_logger_file_handler_encoding(self):
        """Test that file handler uses utf-8 encoding."""
        logger = get_logger("test_logger_encoding")
        from logging.handlers import RotatingFileHandler
        file_handler = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)][0]
        self.assertEqual(file_handler.encoding, "utf-8")

    def test_get_logger_file_handler_rotation(self):
        """Test that file handler has rotation configured."""
        logger = get_logger("test_logger_rotation")
        from logging.handlers import RotatingFileHandler
        file_handler = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)][0]
        self.assertEqual(file_handler.maxBytes, 1_000_000)
        self.assertEqual(file_handler.backupCount, 5)

    def test_get_logger_logging_works(self):
        """Test that logger can actually log messages."""
        logger = get_logger("test_logger_logging")
        try:
            logger.info("Test message")
            logger.debug("Debug message")
            logger.warning("Warning message")
            logger.error("Error message")
        except Exception as e:
            self.fail(f"Logger raised an exception: {e}")

    def test_get_logger_verbose_and_quiet_mutually_exclusive(self):
        """Test behavior when both verbose and quiet are True (quiet takes precedence)."""
        logger = get_logger("test_logger_conflict", verbose=True, quiet=True)
        console_handler = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)][0]
        # quiet is checked first in the if-elif chain
        self.assertEqual(console_handler.level, logging.ERROR)


if __name__ == "__main__":
    unittest.main()
