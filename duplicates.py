import os
import re
import sys
from collections import defaultdict
from send2trash import send2trash  # pip install send2trash

def normalize_basename(fname: str) -> str:
    stem, ext = os.path.splitext(fname)
    s = stem

    while re.search(r"\s*\(\d+\)$", s):
        s = re.sub(r"\s*\(\d+\)$", "", s)

    s = re.sub(r"\s*-\s*(copy|copia)(\s*\(\d+\))?$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip().casefold()

    return f"{s}{ext.lower()}"

def find_win_style_duplicates(folder_path: str):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    groups = defaultdict(list)
    for f in files:
        groups[normalize_basename(f)].append(f)
    dup_groups = {base: names for base, names in groups.items() if len(names) > 1}
    return files, dup_groups

def move_to_trash(dup_groups, folder, auto_confirm=False):
    to_delete = []
    for names in dup_groups.values():
        for n in names:
            if re.search(r"\(\d+\)", n) or re.search(r"-\s*(copy|copia)", n, flags=re.IGNORECASE):
                to_delete.append(n)

    if not to_delete:
        print("No duplicate files to move to trash.")
        return

    print(f"\nFound {len(to_delete)} duplicate files:")
    for f in to_delete:
        print(f"  {f}")

    if not auto_confirm:
        choice = input("\nDo you want to delete the duplicates? (Y/n) ").strip().lower()
        if choice == 'n':
            print("Operation cancelled.")
            return

    for f in to_delete:
        try:
            send2trash(os.path.join(folder, f))
            print(f"Moved to trash: {f}")
        except Exception as e:
            print(f"Error moving {f} to trash: {e}")

if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    auto = "-y" in sys.argv

    files, dup_groups = find_win_style_duplicates(folder)

    print(f"Folder: {folder}")
    print(f"Total files: {len(files)}")

    if not dup_groups:
        print("No duplicates found.")
    else:
        print(f"\nFound {len(dup_groups)} duplicate groups.")
        for base, names in sorted(dup_groups.items()):
            print(f"- Base: {base}")
            for n in sorted(names):
                print(f"    • {n}")

        move_to_trash(dup_groups, folder, auto_confirm=auto)
