
# !/usr/bin/python3
import subprocess


def main():
    # Befehl zum Aktivieren der virtuellen Umgebung
    activate_cmd = 'venv\\Scripts\\activate'
    # Befehl zum Ausführen des Python-Skripts
    script_cmd = 'python.exe main.py --p1x -0.4 --p1y -3 --p2x 0.4 --p2y -0.5 --dir "" --angle 45'
    # Kombinieren Sie die Befehle zu einem einzigen Befehl
    combined_cmd = f'{activate_cmd} && {script_cmd}'
    # Führen Sie den kombinierten Befehl im subprocess aus
    subprocess.run(combined_cmd, shell=True)
    print("Done")
if __name__ == "__main__":
    main()
