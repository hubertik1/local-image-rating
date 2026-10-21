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

### Choose the best of 3 mode
In `Choose the best of 3`, all available images are shuffled once when the session
starts and split into sets of up to 3. Click an image to save the choice and
immediately continue to the next set. Use `Previous` to revisit a set
and replace its selection.

The CSV contains one row per chosen image and only the columns `name`,
`test_option`, and `image_name`. It does not contain the other images from a set.
The file name starts with `results_best_of_three_`.

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
- use the browser Back / Forward buttons or the URL query parameters to revisit a step
- click `Finish` when done and confirm save

7. Get results:
- CSV is saved in `output/`
- file name format:
  `results_<DDMMYYYY_HHMMSS>_<name>.csv`

### Notes
- If `new_images/` is empty, the app will not start rating.
- The first run can take longer because dependencies are installed.
- Navigation state is reflected in the URL, for example `?page=setup`,
  `?page=rating&index=2`, and `?page=finished`. Rating URLs work within the
  current browser session because unsaved ratings are kept in Streamlit session state.

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

### Tryb wyboru najlepszego z 3
W trybie `Choose the best of 3` wszystkie dostepne obrazy sa tasowane jeden raz
przy rozpoczeciu sesji i dzielone na zestawy po maksymalnie 3. Kliknij wybrany
obraz, aby zapisac wybor i od razu przejsc dalej. Przycisk
`Previous` pozwala wrocic do zestawu i zmienic wybor.

CSV zawiera jeden wiersz na wybrany obraz i tylko kolumny `name`, `test_option`
oraz `image_name`. Pozostale obrazy z zestawu nie sa zapisywane. Nazwa pliku
zaczyna sie od `results_best_of_three_`.

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
- uzywaj przyciskow Wstecz / Dalej przegladarki albo parametrow URL, aby wrocic do etapu
- kliknij `Finish` na koncu i potwierdz zapis

7. Odbierz wyniki:
- CSV zapisuje sie w `output/`
- format nazwy pliku:
  `results_<DDMMYYYY_HHMMSS>_<name>.csv`

### Uwagi
- Jesli `new_images/` jest pusty, nie da sie zaczac oceniania.
- Pierwsze uruchomienie moze trwac dluzej, bo instaluja sie zaleznosci.
- Stan nawigacji jest widoczny w URL, np. `?page=setup`,
  `?page=rating&index=2` i `?page=finished`. Adres etapu oceniania dziala w
  aktualnej sesji przegladarki, bo niezapisane oceny sa przechowywane przez Streamlit.
