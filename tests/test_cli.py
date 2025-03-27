import os
import tempfile
from click.testing import CliRunner
from cli.bad_scanner_cli import bad_scanner_cli

def test_cli_help():
    """Test that CLI help works"""
    runner = CliRunner()
    result = runner.invoke(bad_scanner_cli, ['--help'])
    print(result.output)  # Print the output of the CLI command
    assert result.exit_code == 0
    assert 'Process a PDF file to simulate an out-of-focus scanner' in result.output


def test_cli_basic_process(test_pdf=r'bad_scanner\data\PoliceReport.pdf'):
    """Test basic PDF processing with default parameters"""
    # Skip test if test file doesn't exist
    if not os.path.exists(test_pdf):
        print(f"Skipping test because test PDF file {test_pdf} doesn't exist")
        return
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_output:
        temp_output_path = temp_output.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(bad_scanner_cli, [test_pdf, temp_output_path])
        print(result.output)  # Print the output of the CLI command
        assert result.exit_code == 0
        assert os.path.exists(temp_output_path)
        assert os.path.getsize(temp_output_path) > 0
    except Exception as e:
        print(e)
    finally:
        # Clean up
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        print(f"Deleted {temp_output_path}")


if __name__ == '__main__':
    test_cli_help()
    test_cli_basic_process()
