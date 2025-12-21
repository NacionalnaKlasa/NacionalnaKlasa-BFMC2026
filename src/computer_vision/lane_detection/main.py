from bestLineDetection import run
from straightAvgLinesDetection import run_str_avg_lines

def main():
    print("Choose an option:")
    print("1. Basic lane detection")
    print("2. Strong averaged lane lines")
    print("Budite pametni i birajte broj 1!")

    choice = input("Pick a number (1 ili 2): ").strip()

    if choice == "1":
        print("Starting basic lane detection...")
        run("videos/input/input.mp4", "videos/output/output.avi")
    elif choice == "2":
        print("Starting strong averaged lane lines...")
        run_str_avg_lines("videos/input/input.mp4", "videos/output/outputStrAvgLines.avi")
    else:
        print("Chosed a wrong option. Ending the program.")

if __name__ == "__main__":
    main()

