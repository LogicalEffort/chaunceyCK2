import sys
from chaunceyck2.constants import MODEL
from chaunceyck2.agent import build_agent, ask


if __name__ == "__main__":
    agent = build_agent()
    if len(sys.argv) > 1:
        print(ask(agent, " ".join(sys.argv[1:])))
    else:
        print(f"Chauncey ({MODEL}) ready. Ctrl+C to quit.")
        while True:
            try:
                q = input("\nYou: ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if q:
                print("Chauncey:", ask(agent, q))
