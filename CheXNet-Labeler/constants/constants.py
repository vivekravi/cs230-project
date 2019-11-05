from pathlib import Path

# Paths
HOME_DIR = Path.home()
PARSING_MODEL_DIR = HOME_DIR / ".local/share/bllipparser/GENIA+PubMed"

# Observation constants
CARDIOMEGALY = "Cardiomegaly"
ENLARGED_CARDIOMEDIASTINUM = "Enlarged Cardiomediastinum"
SUPPORT_DEVICES = "Support Devices"
NO_FINDING = "No Finding"
OBSERVATION = "observation"
# CATEGORIES = ["No Finding", "Enlarged Cardiomediastinum", "Cardiomegaly",
#               "Lung Lesion", "Lung Opacity", "Edema", "Consolidation",
#               "Pneumonia", "Atelectasis", "Pneumothorax", "Pleural Effusion",
#               "Pleural Other", "Fracture", "Support Devices"]
# Only using the labes that are in CheXNet model.
CATEGORIES = ["No Finding", "Atelectasis", "Cardiomegaly", "Pleural Effusion", 
              "Pneumonia", "Pneumothorax", "Consolidation",
              "Edema"]
# Numeric constants
POSITIVE = 1
NEGATIVE = 0
UNCERTAIN = -1

# Misc. constants
UNCERTAINTY = "uncertainty"
NEGATION = "negation"
REPORTS = "Reports"
