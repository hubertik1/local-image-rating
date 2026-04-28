# Local Image Rating App

## English

### What this app does
This is a local Streamlit app for manual image evaluation.
You add images to `new_images/`, review them one by one, and save results as CSV files in `output/`.

### Supported image formats
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

### Labels from folders (optional)
You can organize images in subfolders, for example:

- `new_images/amusement/...`
- `new_images/awe/...`

Then you can enable `Show labels` in the app to display the folder name as a label.

### 3-image quality mode
The app also supports rating images in sets of up to 3. Add files with the same
base name and suffixes `_1`, `_2`, `_3`, for example:

- `new_images/image_1.jpg`
- `new_images/image_2.jpg`
- `new_images/image_3.jpg`

Choose `3-image quality rating` to see the available images side by side. Each image
gets its own quality score (`1`, `0.5`, `0`) and optional comment. The CSV output stores
one row per set with columns `image_name_1`, `quality_score_1`, `comment_1`, and so on.
If a set has only one or two files, the app still shows and saves the available images.

### Step-by-step usage
Repository URL: `https://github.com/hubertik1/local-image-rating`

1. Clone the repository:
```bash
git clone https://github.com/hubertik1/local-image-rating
cd local-image-rating
```

2. Add images to `new_images/`:
- flat structure: `new_images/img1.jpg`
- or with label folders: `new_images/label_name/img1.jpg`

3. Start the app:
- macOS/Linux: double-click `START_MAC_LINUX.command`
- Windows: double-click `START_WINDOWS.bat`

4. Wait for first-time setup:
- script creates `venv/` (if missing)
- installs dependencies from `requirements.txt`
- starts Streamlit at `http://localhost:8501`

5. In the app:
- enter your name
- choose test type
- (for emotion mode) choose emotions
- click `Start`

6. Rate images:
- use `Previous` / `Next`
- click `Finish` when done and confirm save

7. Get results:
- CSV is saved in `output/`
- file name format:
  `results_<DDMMYYYY_HHMMSS>_<name>.csv`

### Notes
- If `new_images/` is empty, the app will not start rating.
- The first run can take longer because dependencies are installed.

---

## Polski

### Co robi aplikacja
To lokalna aplikacja Streamlit do recznej oceny obrazow.
Dodajesz obrazy do `new_images/`, oceniasz je po kolei i zapisujesz wyniki jako CSV w `output/`.

### Obslugiwane formaty obrazow
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

### Label z folderow (opcjonalnie)
Mozesz ulozyc obrazy w podfolderach, np.:

- `new_images/amusement/...`
- `new_images/awe/...`

Wtedy po wlaczeniu `Show labels` aplikacja pokazuje nazwe folderu jako label.

### Tryb jakosci dla 3 obrazow
Aplikacja obsluguje tez ocenianie kompletow do 3 obrazow. Dodaj pliki z ta sama
nazwa bazowa i koncowkami `_1`, `_2`, `_3`, na przyklad:

- `new_images/image_1.jpg`
- `new_images/image_2.jpg`
- `new_images/image_3.jpg`

Wybierz `3-image quality rating`, aby zobaczyc dostepne obrazy obok siebie. Kazdy
obraz ma wlasny wybor jakosci (`1`, `0.5`, `0`) i opcjonalny komentarz. CSV zapisuje
jeden wiersz na komplet z kolumnami `image_name_1`, `quality_score_1`, `comment_1` itd.
Jesli komplet ma tylko jeden albo dwa pliki, aplikacja nadal pokazuje i zapisuje
dostepne obrazy.

### Uzycie krok po kroku
URL repozytorium: `https://github.com/hubertik1/local-image-rating`

1. Sklonuj repozytorium:
```bash
git clone https://github.com/hubertik1/local-image-rating
cd local-image-rating
```

2. Wrzuc obrazy do `new_images/`:
- bez folderow: `new_images/img1.jpg`
- albo z folderami labeli: `new_images/nazwa_labelu/img1.jpg`

3. Uruchom aplikacje:
- macOS/Linux: dwuklik na `START_MAC_LINUX.command`
- Windows: dwuklik na `START_WINDOWS.bat`

4. Poczekaj na pierwsze uruchomienie:
- skrypt tworzy `venv/` (jesli brak)
- instaluje zaleznosci z `requirements.txt`
- uruchamia Streamlit pod `http://localhost:8501`

5. W aplikacji:
- wpisz imie
- wybierz typ testu
- (dla trybu emocji) wybierz emocje
- kliknij `Start`

6. Oceniaj obrazy:
- uzywaj `Previous` / `Next`
- kliknij `Finish` na koncu i potwierdz zapis

7. Odbierz wyniki:
- CSV zapisuje sie w `output/`
- format nazwy pliku:
  `results_<DDMMYYYY_HHMMSS>_<name>.csv`

### Uwagi
- Jesli `new_images/` jest pusty, nie da sie zaczac oceniania.
- Pierwsze uruchomienie moze trwac dluzej, bo instaluja sie zaleznosci.
