
import sys
import os

sys.path.append(os.getcwd())

from rag.lookup import get_player_by_reg_id

def verify(reg_id):
    print(f"--- Verifying Profile for {reg_id} ---")
    result = get_player_by_reg_id(reg_id)
    print(result)

if __name__ == "__main__":
    verify("SATGCMC-01160700070")
