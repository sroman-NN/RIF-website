import os
import shutil
import tempfile
from pathlib import Path
import pytest
from rif.dedicated import create_dedicated_compiler


def test_create_dedicated_compiler_target_packaging():
    """Test that dedicated compiler generation creates launcher scripts and target packages correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "test_compiler"
        
        # We target gba since it exists in the codebase
        result = create_dedicated_compiler(
            "gba",
            output=output_dir,
            make_exe=False,
            compiler_name="MyTestGbaCompiler",
            target_os="linux",
            target_arch="amd64"
        )
        
        # Verify result dataclass
        assert result.plugin == "gba"
        assert result.root == output_dir
        
        # Verify launcher scripts and python file exist
        assert (output_dir / "MyTestGbaCompiler.py").exists()
        assert (output_dir / "MyTestGbaCompiler").exists()  # sh launcher
        assert (output_dir / "MyTestGbaCompiler.bat").exists()  # bat launcher
        
        # Verify autonomous rif copy
        assert (output_dir / "rif").exists()
        assert (output_dir / "rif" / "__init__.py").exists()
        
        # Verify zip package creation
        zip_path = Path(tmpdir) / "MyTestGbaCompiler-linux-amd64.zip"
        assert zip_path.exists()


def test_get_plugin_extension():
    """Test that _get_plugin_extension finds and parses ext.* files correctly."""
    from rif.dedicated import _get_plugin_extension
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = Path(tmpdir)
        
        # Test when no ext.* exists
        assert _get_plugin_extension(plugin_dir) is None
        
        # Test ext.gbasm
        ext_file = plugin_dir / "ext.gbasm"
        ext_file.touch()
        assert _get_plugin_extension(plugin_dir) == ".gbasm"
        
        # Test priority (alphabetical/sorted due to sorted(iterdir()))
        ext_file2 = plugin_dir / "ext.myext"
        ext_file2.touch()
        # Since sorted order: ext.gbasm comes before ext.myext
        assert _get_plugin_extension(plugin_dir) == ".gbasm"
        
        # Remove ext.gbasm, should get .myext
        ext_file.unlink()
        assert _get_plugin_extension(plugin_dir) == ".myext"

