import unittest
from pathlib import Path
import tempfile
import shutil
from zoomtube.utils.recordings import get_unique_filename, select_preferred_recording, sanitize_filename


class TestSelectPreferredRecording(unittest.TestCase):
    def test_select_shared_screen_with_gallery_view(self):
        """Test that shared_screen_with_gallery_view is selected first."""
        files = [
            {"file_type": "MP4", "recording_type": "gallery_view"},
            {"file_type": "MP4", "recording_type": "shared_screen_with_gallery_view"},
        ]
        result = select_preferred_recording(files)
        self.assertEqual(result.get("recording_type"), "shared_screen_with_gallery_view")

    def test_select_shared_screen_with_speaker_view(self):
        """Test that shared_screen_with_speaker_view is selected when gallery not available."""
        files = [
            {"file_type": "MP4", "recording_type": "gallery_view"},
            {"file_type": "MP4", "recording_type": "shared_screen_with_speaker_view"},
        ]
        result = select_preferred_recording(files)
        self.assertEqual(result.get("recording_type"), "shared_screen_with_speaker_view")

    def test_select_active_speaker(self):
        """Test that active_speaker is selected when higher priority types not available."""
        files = [
            {"file_type": "MP4", "recording_type": "gallery_view"},
            {"file_type": "MP4", "recording_type": "active_speaker"},
        ]
        result = select_preferred_recording(files)
        self.assertEqual(result.get("recording_type"), "active_speaker")

    def test_select_gallery_view(self):
        """Test that gallery_view is selected as last option."""
        files = [
            {"file_type": "MP4", "recording_type": "gallery_view"},
        ]
        result = select_preferred_recording(files)
        self.assertEqual(result.get("recording_type"), "gallery_view")

    def test_ignore_non_mp4_files(self):
        """Test that non-MP4 files are ignored."""
        files = [
            {"file_type": "M4A", "recording_type": "shared_screen_with_gallery_view"},
            {"file_type": "MP4", "recording_type": "gallery_view"},
        ]
        result = select_preferred_recording(files)
        self.assertEqual(result.get("recording_type"), "gallery_view")

    def test_no_matching_recording(self):
        """Test that None is returned when no MP4 recording found."""
        files = [
            {"file_type": "M4A", "recording_type": "active_speaker"},
        ]
        result = select_preferred_recording(files)
        self.assertIsNone(result)

    def test_empty_list(self):
        """Test that None is returned for empty file list."""
        result = select_preferred_recording([])
        self.assertIsNone(result)


class TestGetUniqueFilename(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_get_unique_filename_new_file(self):
        """Test that the original filename is returned when file doesn't exist."""
        result = get_unique_filename(self.output_path, "test.txt")
        self.assertEqual(result.name, "test.txt")

    def test_get_unique_filename_existing_file(self):
        """Test that a numbered filename is returned when file exists."""
        # Create a file
        test_file = self.output_path / "test.txt"
        test_file.write_text("content")
        
        result = get_unique_filename(self.output_path, "test.txt")
        self.assertEqual(result.name, "test (1).txt")

    def test_get_unique_filename_multiple_existing_files(self):
        """Test that correct numbering is applied for multiple existing files."""
        # Create multiple files
        (self.output_path / "test.txt").write_text("content")
        (self.output_path / "test (1).txt").write_text("content")
        
        result = get_unique_filename(self.output_path, "test.txt")
        self.assertEqual(result.name, "test (2).txt")

    def test_creates_directory_if_not_exists(self):
        """Test that the output directory is created if it doesn't exist."""
        nested_path = Path(self.temp_dir) / "nested" / "dir"
        result = get_unique_filename(nested_path, "file.txt")
        self.assertTrue(nested_path.exists())

    def test_get_unique_filename_no_extension(self):
        """Test that files without extension are handled correctly."""
        result = get_unique_filename(self.output_path, "README")
        self.assertEqual(result.name, "README")

    def test_get_unique_filename_no_extension_existing(self):
        """Test numbering for files without extension."""
        (self.output_path / "README").write_text("content")
        result = get_unique_filename(self.output_path, "README")
        self.assertEqual(result.name, "README (1)")


class TestSanitizeFilename(unittest.TestCase):
    def test_sanitize_invalid_characters(self):
        """Test that invalid characters are replaced with underscores."""
        result = sanitize_filename('file<name>.txt')
        self.assertEqual(result, 'file_name_.txt')

    def test_sanitize_multiple_invalid_chars(self):
        """Test that multiple invalid characters are all replaced."""
        result = sanitize_filename('file:name|path?test*')
        self.assertEqual(result, 'file_name_path_test_')

    def test_sanitize_quotes(self):
        """Test that quotes are replaced."""
        result = sanitize_filename('file"name\\test')
        self.assertEqual(result, 'file_name_test')

    def test_sanitize_backslash_and_forward_slash(self):
        """Test that slashes are replaced."""
        result = sanitize_filename('file\\name/test')
        self.assertEqual(result, 'file_name_test')

    def test_sanitize_preserves_valid_chars(self):
        """Test that valid characters are preserved."""
        result = sanitize_filename('file-name_123.txt')
        self.assertEqual(result, 'file-name_123.txt')

    def test_sanitize_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        result = sanitize_filename('  filename  ')
        self.assertEqual(result, 'filename')

    def test_sanitize_empty_string(self):
        """Test that empty string is handled."""
        result = sanitize_filename('')
        self.assertEqual(result, '')

    def test_sanitize_all_invalid_chars(self):
        """Test filename with only invalid characters."""
        result = sanitize_filename('<>:"/\\|?*')
        self.assertEqual(result, '_________')


if __name__ == "__main__":
    unittest.main()
