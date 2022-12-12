## v1.0.0 (2022-12-12)

### Feat

- **src/api/**: Implemented CRUD Rest API for recipes
- **src/api/**: Fixed POST method for creating a request, as well as GET methods for all recipes and all ingredients
- First working version of POST API for recipes
- Improvements to the Recipes API
- **src/base/model.py**: Added methods to save and load model
- **src/api/**: Added initial version of Flask API
- Added MySQL queries to create new user and set up `recipes` schema
- **notebooks/1-eda-model.ipynb**: Added notebook for EDA and model training and testing
- **src/base/**: Added source code for Linear Regression model and data preprocessing

### Fix

- **notebooks/1-eda-model.ipynb**: Fixed a bug in model training that was using the target variable as input
