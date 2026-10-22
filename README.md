# Local Image Rating App

## English

### What this app does
This is a local Streamlit app for manual image evaluation.
Choose an image folder anywhere on your computer, review the images, and save results as CSV files in `output/`.

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

### Choose a folder to evaluate
On the front page, click the prominent `Browse computer…` button in `Choose images`,
above the name and test settings. Use `Jump to` for a drive
or common location, select a subfolder and click `Open`, or enter a `Folder path`.
Click `Use this folder` to load its images directly; copying them is unnecessary.
The browser shows folders on the computer running the app. `Use default folder`
returns to `new_images/`.

Then choose one category or `All folders` before clicking `Start`. Categories are
folders containing images under your chosen location, including nested folders
with their relative paths. `Main folder` means images directly inside that location.
Choosing a category includes only its own images; nested folders remain separate.
The selection applies to all modes and is remembered when starting a new session
in the same browser tab. Each rating session keeps its original image location.

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
In `Choose the best of 3`, images are shuffled separately within each folder when
the session starts and split into sets of up to 3. Sets never mix folders, even
when `All folders` is selected. Any leftover one or two images form their own set
within that folder. The current folder is shown above the images.
Click an image or press `1`, `2`, or `3`
for the corresponding image from the left to save the choice and immediately
continue to the next set. Use `Previous` to revisit a set
and replace its selection. The image columns expand to use the available screen
width. Click `Finish and save CSV` at any time, then confirm, to save your completed
choices without reviewing all sets.

The CSV contains one row for every image in a set with a saved choice. Unreviewed
sets are omitted when finishing early. Its columns are `name`,
`test_option`, `image_name`, and `selected`. The `selected` value is `1` for a
chosen image and `0` for every other image. The file name starts with
`results_best_of_three_`.

### Single-image review mode
Choose `Single-image review` to see one image at a time from the selected folder.
Click `Great!`, `Good concept but needs improvement`, or `Delete` (shortcuts `1`,
`2`, and `3`) to record the rating and advance immediately. `Previous` returns to
the preceding image, highlights its saved rating, and lets you replace it.
`Delete` is a rating only; it does not remove the image file.
The choices stay in a fixed bottom bar: green for `Great!`, amber for improvement,
and red for `Delete`. The full image fits the available screen space above the bar
without cropping, so the buttons stay in the same place for every image.

`Finish and save CSV` is available at any time. The export includes only rated
images, with columns `name`, `test_option`, `image_name`, `image_path`, and `rating`.
The `image_path`, relative to the chosen image location, distinguishes matching file names in different folders.
The file name starts with `results_single_image_review_`.

### Step-by-step usage
Repository URL: `https://github.com/hubertik1/local-image-rating`

1. Clone the repository:
```bash
git clone https://github.com/hubertik1/local-image-rating
cd local-image-rating
```

2. Prepare your image folder anywhere on the computer, or add images to `new_images/`:
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
- If the selected folder has no supported images, choose another folder before starting.
- The first run can take longer because dependencies are installed.
- Navigation state is reflected in the URL, for example `?page=setup`,
  `?page=rating&index=2`, and `?page=finished`. Rating URLs work within the
  current browser session because unsaved ratings are kept in Streamlit session state.

---

## Polski

### Co robi aplikacja
To lokalna aplikacja Streamlit do recznej oceny obrazow.
Wybierasz folder obrazow w dowolnym miejscu na komputerze, oceniasz obrazy i zapisujesz wyniki jako CSV w `output/`.

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

### Wybor folderu do oceny
Na stronie startowej, w sekcji `Choose images` nad imieniem i ustawieniami testu,
kliknij widoczny przycisk `Browse computer…`. Przejdz do dysku lub lokalizacji
przez `Jump to`, wybierz podfolder i kliknij `Open` albo wpisz `Folder path`.
Kliknij `Use this folder`, aby wczytac obrazy bez kopiowania. Przegladarka pokazuje
foldery komputera, na ktorym dziala aplikacja. `Use default folder` wraca do `new_images/`.

Nastepnie wybierz jedna kategorie lub `All folders` i kliknij `Start`. Lista obejmuje
foldery z obrazami we wskazanej lokalizacji, w tym podfoldery oznaczone sciezkami
wzglednymi. `Main folder` oznacza obrazy bezposrednio w wybranej lokalizacji.
Wybor kategorii obejmuje tylko jej obrazy; podfoldery sa osobnymi kategoriami.
Wybor dotyczy wszystkich trybow i pozostaje zapamietany przy nowej sesji w tej samej
karcie przegladarki. Trwajaca sesja zachowuje swoja pierwotna lokalizacje obrazow.

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
W trybie `Choose the best of 3` obrazy sa tasowane osobno w kazdym folderze
przy rozpoczeciu sesji i dzielone na zestawy po maksymalnie 3. Zestawy nigdy nie
mieszaja folderow, takze przy wyborze `All folders`. Pozostale jeden lub dwa obrazy
tworza osobny zestaw w swoim folderze. Nazwa aktualnego folderu jest widoczna nad obrazami.
Kliknij wybrany
obraz albo nacisnij `1`, `2` lub `3` dla odpowiedniej pozycji od lewej, aby
zapisac wybor i od razu przejsc dalej. Przycisk
`Previous` pozwala wrocic do zestawu i zmienic wybor. Kolumny obrazow wykorzystuja
dostepna szerokosc ekranu. Kliknij `Finish and save CSV` w dowolnym momencie
i potwierdz, aby zapisac dokonane wybory bez oceniania wszystkich zestawow.

CSV zawiera jeden wiersz dla kazdego obrazu z zestawu z zapisanym wyborem.
Przy wczesniejszym zakonczeniu nieocenione zestawy sa pomijane. Kolumny to `name`,
`test_option`, `image_name` i `selected`. Wartosc `selected` wynosi `1` dla
wybranego obrazu i `0` dla pozostalych. Nazwa pliku zaczyna sie od
`results_best_of_three_`.

### Tryb oceny pojedynczych obrazow
Wybierz `Single-image review`, aby ogladac po jednym obrazie z wybranego folderu.
Kliknij `Great!`, `Good concept but needs improvement` lub `Delete` (skroty `1`,
`2` i `3`), aby zapisac ocene i od razu przejsc dalej. `Previous` wraca do
poprzedniego obrazu, podswietla zapisana ocene i pozwala ja zmienic.
`Delete` jest tylko ocena; nie usuwa pliku obrazu.
Przyciski pozostaja w stalym dolnym pasku: zielony dla `Great!`, zolty dla poprawy
i czerwony dla `Delete`. Caly obraz wypelnia dostepne miejsce nad paskiem bez
przycinania, a przyciski nie zmieniaja polozenia przy przechodzeniu dalej.

Przycisk `Finish and save CSV` jest dostepny w dowolnym momencie. Eksport obejmuje
tylko ocenione obrazy i zawiera kolumny `name`, `test_option`, `image_name`,
`image_path` i `rating`. Sciezka wzgledna w `image_path` rozroznia pliki o takich
samych nazwach w roznych folderach. Nazwa pliku zaczyna sie od
`results_single_image_review_`.

### Uzycie krok po kroku
URL repozytorium: `https://github.com/hubertik1/local-image-rating`

1. Sklonuj repozytorium:
```bash
git clone https://github.com/hubertik1/local-image-rating
cd local-image-rating
```

2. Przygotuj folder obrazow w dowolnym miejscu na komputerze lub wrzuc obrazy do `new_images/`:
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
- Jesli wybrany folder nie zawiera obslugiwanych obrazow, przed rozpoczeciem wybierz inny folder.
- Pierwsze uruchomienie moze trwac dluzej, bo instaluja sie zaleznosci.
- Stan nawigacji jest widoczny w URL, np. `?page=setup`,
  `?page=rating&index=2` i `?page=finished`. Adres etapu oceniania dziala w
  aktualnej sesji przegladarki, bo niezapisane oceny sa przechowywane przez Streamlit.
