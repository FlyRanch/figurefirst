1. Make sure you are using twine > 1.11. 
   * That means using python 3. To make a virtual environment: `python3 -m venv ENVIRONMENTNAME`
   * `source ENVIRONMENTNAME/bin/activate`
   * Update pip: `pip install --upgrade pip`
   * `pip install twine`
2. make sure setuptools, twine, and wheel are all up-to-date (check version with requirements.txt)
3. Update the version number in setup.py
4. Clear out the /dist directory
5. Run `python setup.py sdist`
6. Run `twine upload dist/*`