"""
Compare feature importances from Random Forest and Logistic Regression.
Generates a merged table and a barplot for visual analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt

# Paths to feature importance files
rf_path = '../Datathon Decision/4_gold/feature_importance_rf.csv'
lr_path = '../Datathon Decision/4_gold/feature_importance_lr.csv'

# Load feature importances
df_rf = pd.read_csv(rf_path, index_col=0, header=0, names=['feature', 'rf_importance'])
df_lr = pd.read_csv(lr_path, index_col=0, header=0, names=['feature', 'lr_coef'])

# Merge on feature name
df = df_rf.join(df_lr, how='outer')

# Add absolute value of LR coefficients for comparison
df['lr_coef_abs'] = df['lr_coef'].abs()

# Sort by RF importance and LR abs(coef)
df_sorted_rf = df.sort_values('rf_importance', ascending=False)
df_sorted_lr = df.sort_values('lr_coef_abs', ascending=False)

# Save merged table
out_csv = '../Datathon Decision/4_gold/feature_importance_comparison.csv'
df.to_csv(out_csv)
print(f'Merged feature importance table saved to {out_csv}')

# Plot top 15 features by each method
N = 15
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Random Forest
axes[0].barh(
    df_sorted_rf.head(N).index[::-1], df_sorted_rf.head(N)['rf_importance'][::-1]
)
axes[0].set_title('Top 15 Features - Random Forest')
axes[0].set_xlabel('Importance')

# Logistic Regression (absolute value)
axes[1].barh(
    df_sorted_lr.head(N).index[::-1], df_sorted_lr.head(N)['lr_coef_abs'][::-1]
)
axes[1].set_title('Top 15 Features - Logistic Regression (|coef|)')
axes[1].set_xlabel('|Coefficient|')

plt.tight_layout()
plot_path = '../Datathon Decision/4_gold/feature_importance_comparison.png'
plt.savefig(plot_path)
print(f'Feature importance comparison plot saved to {plot_path}')
