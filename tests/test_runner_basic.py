"""Basic tests for lambdora.runner module."""


def test_runner_import():
    """Test that runner module can be imported and functions exist."""
    from lambdora.runner import load_std, run_file

    assert callable(run_file)
    assert callable(load_std)


def test_load_std_basic():
    """Test basic load_std functionality."""
    from lambdora.runner import load_std

    # Should not raise an error
    load_std()
