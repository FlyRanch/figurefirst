1. Make sure you are using twine > 1.11. 
   * That means using python 3. To make a virtual environment: `python3 -m venv ENVIRONMENTNAME`
   * `pip install twine`
2. Update the version number in setup.py
3. Clear out the /dist directory
4. Run `python3 setup.py sdist`
5. Run `twine upload dist/*`