import numpy as np
import pandas as pd

# Parameters for data generation
num_features = 4  # Number of floating-point features (A-D)
num_records = 100  # Number of rows
num_categories = 4  # Number of classes/categories (1, 2, 3, 4)

# Generate random floating-point feature values between 0 and 1
features = np.random.rand(num_records, num_features)

# Generate random integer labels (classes) between 1 and `num_categories`
labels = np.random.randint(1, num_categories + 1, size=(num_records, 1))  # Ensure labels are integers

# Combine features and labels
data = np.hstack([features, labels])

# Create a DataFrame
df = pd.DataFrame(data)

# Format the last column (labels) as integers
df.iloc[:, -1] = df.iloc[:, -1].astype(int)

# Save to CSV
output_path = 'energy_consumption.csv'
with open(output_path, 'w') as f:
    # Write rows one at a time, applying specific formats
    for row in df.itertuples(index=False, name=None):
        formatted_row = ','.join([f"{x:.6f}" if isinstance(x, float) else str(x) for x in row])
        f.write(formatted_row + '\n')

print(f"CSV file saved to {output_path}")
