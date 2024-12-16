"""
Script to verify MongoDB installation and status
"""
from utils.db_validator import validate_mongodb_installation

if __name__ == "__main__":
    validate_mongodb_installation()