import os

PREMIUM_BRANDS = ["MICHELIN", "PIRELLI", "DUNLOP", "CONTINENTAL", "GOODYEAR", "BRIDGESTONE"]

BUDGET_BRANDS = ["KUHMO", "NEXEN", "BARUM", "WANLI", "STARMAXX", "HANKOOK", "FALKEN", "FORTUNA", "MATADOR"]

OUTPUT_PATH = "./html_files"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = BASE_DIR + "/templates/static/"