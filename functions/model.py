import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split


# Create a category for a variable with percentiles rule
def create_categories(data, column):
    # Calculate the percentiles
    q25 = np.percentile(data['capital_social'], 25)
    median = np.median(data['capital_social'])
    q75 = np.percentile(data['capital_social'], 75)

    # Create a new column based on the conditions
    data[f'{column}_cat'] = data[column].apply(lambda x: 0 if x < q25 else (1 if x < median else (2 if x < q75 else 3)))


# Perform a robust regression using statsmodels
def robust_regression_sm(df_temp_i, target, independents, test_size=0.2):
    X = df_temp_i[independents]
    y = df_temp_i[[target]]
    X = sm.add_constant(X)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    huber_wls = sm.RLM(y_train, X_train, M=sm.robust.norms.HuberT())

    model = huber_wls.fit()
    y_hat = model.predict(X_test)

    # Calculate and print important metrics
    r_squared = r2_score(y_test, y_hat)
    mse = mean_squared_error(y_test, y_hat)
    mae = mean_absolute_error(y_test, y_hat)
    print('Test Set Results:')
    print('R-squared:', r_squared)
    print('Mean Squared Error (MSE):', mse)
    print('Mean Absolute Error (MAE):', mae)
    
    # Save the results to a file
    summary_results = model.summary()
    with open('../outputs/summary_results.csv', 'w') as f:
        f.write(str(summary_results))

    test_results = pd.DataFrame({
        'Metric': ['R-squared', 'Mean Squared Error (MSE)', 'Mean Absolute Error (MAE)'],
        'Value': [r_squared, mse, mae]
    })
    test_results.to_csv('../outputs/test_results.csv', index=False)
    
    
    return summary_results