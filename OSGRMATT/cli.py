import sys
from pathlib import Path
import os
import shutil


def copy_file(file_name: str):
    base_dir = Path(__file__).parent.resolve()
    user_project_root = os.getcwd()
    source_file = base_dir / file_name
    shutil.copyfile(source_file, user_project_root + f'/{file_name}')


def create_ini_file():
    pytest_ini_path = Path.cwd() / 'pytest.ini'
    with open(pytest_ini_path, 'w') as f:
        f.write('[pytest]\n')
        f.write('addopts = --html=html_reports/report_api_test.html --log-cli-level=INFO --capture=tee-sys  '
                '--self-contained-html\n')


def create_api_project():
    """Create API project structure."""
    project_dir = Path.cwd()
    for folder in ('endpoints', 'tests', 'configs', 'html_reports', 'response_jsons', 'test_data'):
        Path(project_dir / folder).mkdir(parents=True, exist_ok=True)
        open(project_dir / folder / '__init__.py', 'a').close()

    create_ini_file()
    copy_file('conftest.py')


def create_selenium_project():
    """Create Selenium project structure."""
    project_dir = Path.cwd()

    for folder in ('pages', 'processes', 'tests', 'configs', 'html_reports'):
        Path(project_dir / folder).mkdir(exist_ok=True)
        open(project_dir / folder / '__init__.py', 'a').close()

    tmp_dir = Path.cwd() / 'tmp'
    tmp_dir.mkdir(exist_ok=True)
    for subfolder in ('downloads', 'screencasts', 'screenshots'):
        Path(tmp_dir / subfolder).mkdir(parents=True, exist_ok=True)
        open(tmp_dir / subfolder / '__init__.py', 'a').close()

    create_ini_file()
    copy_file('conftest.py')


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'create_api_project':
            create_api_project()
        elif command == 'create_selenium_project':
            create_selenium_project()
    else:
        print("Необходимо указать команду для создания проекта.")


if __name__ == '__main__':
    main()
