import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from imblearn.over_sampling import SMOTE

# Charger les données
data = pd.read_csv('stress_management/stress_data.csv', sep=';', encoding='ISO-8859-1')

# Encoder la cible (label) 'Niveau de Stress'
le = LabelEncoder()
data['Niveau de Stress'] = le.fit_transform(data['Niveau de Stress'])

# Séparer les caractéristiques et les étiquettes
X = data.drop('Niveau de Stress', axis=1)
y = data['Niveau de Stress']

# Encoder toutes les colonnes non numériques dans X
X = X.apply(lambda col: le.fit_transform(col) if col.dtype == 'object' else col)

# Sur-échantillonnage
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Diviser les données en ensembles d'entraînement et de test avec stratification
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled)

# Initialiser le modèle
model = DecisionTreeClassifier(random_state=42)

# Hyperparameter tuning
param_grid = {
    'max_depth': [3, 5, 10, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
}
grid_search = GridSearchCV(model, param_grid, cv=5)
grid_search.fit(X_train, y_train)

# Meilleur modèle
model = grid_search.best_estimator_

# Afficher la précision
accuracy = model.score(X_test, y_test)
print(f"Précision sur l'ensemble de test : {accuracy:.2f}")

# Évaluation
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, labels=le.transform(le.classes_), target_names=le.classes_, zero_division=1))
print(confusion_matrix(y_test, y_pred))

# Sauvegarder le modèle et l'encodeur
joblib.dump(model, 'stress_management/models/stress_model.pkl')
joblib.dump(le, 'stress_management/models/label_encoder.pkl')

print("Modèle et encodeur sauvegardés avec succès.")
