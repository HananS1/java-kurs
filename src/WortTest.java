import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.Scanner;

/**
 * Erzeugt fertige Wort-Tests zum Kopieren nach Word.
 *
 * Jeder Test hat 7 Fragen mit je 3 Antworten. Die richtige Antwort steht
 * mal an erster, mal an zweiter, mal an dritter Stelle - in jeder Runde
 * kommt jede Position mindestens einmal vor.
 *
 * Bereits gestellte Wörter merkt sich das Programm in einer Datei und
 * fragt sie kein zweites Mal. Für die schon gestellten gibt es den
 * Wiederholungstest.
 */
public class WortTest {

    static final int FRAGEN_PRO_TEST = 7;
    static final Path GEDAECHTNIS = Path.of("gefragte-woerter.txt");
    static final Path AUSGABE = Path.of("wort-test.txt");

    static final Random ZUFALL = new Random();

    public static void main(String[] args) {
        Scanner eingabe = new Scanner(System.in);
        boolean laeuft = true;

        while (laeuft) {
            List<String> gefragt = ladeGefragte();
            int offen = Wortschatz.EINTRAEGE.length - gefragt.size();

            System.out.println();
            System.out.println("=== Wort Test ===");
            System.out.println(gefragt.size() + " von " + Wortschatz.EINTRAEGE.length
                    + " Wörtern gespielt, " + offen + " noch frisch");
            System.out.println("(1) Neuer Test");
            System.out.println("(2) Wiederholungstest");
            System.out.println("(3) Gemerkte Wörter zurücksetzen");
            System.out.println("(4) Beenden");

            String wahl = eingabe.nextLine().trim();

            if (wahl.equals("1")) {
                neuerTest(gefragt);
            } else if (wahl.equals("2")) {
                wiederholungsTest(gefragt);
            } else if (wahl.equals("3")) {
                speichereGefragte(new ArrayList<>());
                System.out.println("Gedächtnis geleert. Alle Wörter sind wieder frisch.");
            } else if (wahl.equals("4")) {
                laeuft = false;
            } else {
                System.out.println("Bitte 1, 2, 3 oder 4 eingeben.");
            }
        }

        eingabe.close();
        System.out.println("Bis zum nächsten Video!");
    }

    /** Zieht Wörter, die noch nie an der Reihe waren. */
    static void neuerTest(List<String> gefragt) {
        List<String> vorrat = new ArrayList<>();
        for (String eintrag : Wortschatz.EINTRAEGE) {
            if (!gefragt.contains(wortVon(eintrag))) {
                vorrat.add(eintrag);
            }
        }

        if (vorrat.isEmpty()) {
            System.out.println("Alle Wörter sind durch! Nimm den Wiederholungstest (2)");
            System.out.println("oder setze das Gedächtnis zurück (3).");
            return;
        }

        List<String> auswahl = zieheZufaellig(vorrat, FRAGEN_PRO_TEST);
        for (String eintrag : auswahl) {
            gefragt.add(wortVon(eintrag));
        }
        speichereGefragte(gefragt);

        zeigeTest("Wort Test", auswahl);
    }

    /** Stellt Wörter noch einmal, die schon einmal dran waren. */
    static void wiederholungsTest(List<String> gefragt) {
        List<String> vorrat = new ArrayList<>();
        for (String eintrag : Wortschatz.EINTRAEGE) {
            if (gefragt.contains(wortVon(eintrag))) {
                vorrat.add(eintrag);
            }
        }

        if (vorrat.isEmpty()) {
            System.out.println("Noch nichts zu wiederholen. Mach erst einen neuen Test (1).");
            return;
        }

        zeigeTest("Wiederholungstest", zieheZufaellig(vorrat, FRAGEN_PRO_TEST));
    }

    /** Baut den fertigen Text, zeigt ihn an und legt ihn als Datei ab. */
    static void zeigeTest(String titel, List<String> auswahl) {
        int[] plan = positionsPlan(auswahl.size());
        StringBuilder text = new StringBuilder();

        text.append(zentriert(titel)).append(System.lineSeparator());

        for (int i = 0; i < auswahl.size(); i++) {
            String[] teile = auswahl.get(i).split("\\|");
            String wort = teile[0];
            String richtig = teile[1];

            List<String> falsche = new ArrayList<>();
            falsche.add(teile[2]);
            falsche.add(teile[3]);
            Collections.shuffle(falsche, ZUFALL);

            text.append((i + 1)).append(")     Was bedeutet „").append(wort).append("“?")
                .append(System.lineSeparator());

            int naechsteFalsche = 0;
            for (int platz = 0; platz < 3; platz++) {
                if (platz == plan[i]) {
                    text.append("         ○ ").append(richtig).append(" ✓");
                } else {
                    text.append("         ○ ").append(falsche.get(naechsteFalsche));
                    naechsteFalsche++;
                }
                text.append(System.lineSeparator());
            }
        }

        System.out.println();
        System.out.print(text);

        try {
            Files.writeString(AUSGABE, text.toString(), StandardCharsets.UTF_8);
            System.out.println();
            System.out.println("Auch gespeichert in: " + AUSGABE.toAbsolutePath());
        } catch (IOException e) {
            System.out.println();
            System.out.println("Konnte die Datei nicht schreiben: " + e.getMessage());
            System.out.println("Du kannst den Test oben trotzdem direkt kopieren.");
        }
    }

    /**
     * Legt fest, an welcher Stelle die richtige Antwort steht.
     *
     * Die drei Plätze werden so gleichmäßig wie möglich verteilt, gemischt,
     * und direkt aufeinanderfolgende gleiche Plätze werden aufgebrochen -
     * sonst entsteht ein Muster, das man beim Zuschauen erkennt.
     */
    static int[] positionsPlan(int anzahl) {
        int[] wieOft = {anzahl / 3, anzahl / 3, anzahl / 3};

        List<Integer> reihenfolge = new ArrayList<>(List.of(0, 1, 2));
        Collections.shuffle(reihenfolge, ZUFALL);
        for (int i = 0; i < anzahl - (anzahl / 3) * 3; i++) {
            wieOft[reihenfolge.get(i)]++;
        }

        List<Integer> plan = new ArrayList<>();
        for (int platz = 0; platz < 3; platz++) {
            for (int k = 0; k < wieOft[platz]; k++) {
                plan.add(platz);
            }
        }
        Collections.shuffle(plan, ZUFALL);

        for (int i = 1; i < plan.size(); i++) {
            if (!plan.get(i).equals(plan.get(i - 1))) {
                continue;
            }
            for (int j = i + 1; j < plan.size(); j++) {
                if (!plan.get(j).equals(plan.get(i)) && !plan.get(j).equals(plan.get(i - 1))) {
                    Collections.swap(plan, i, j);
                    break;
                }
            }
        }

        int[] ergebnis = new int[anzahl];
        for (int i = 0; i < anzahl; i++) {
            ergebnis[i] = plan.get(i);
        }
        return ergebnis;
    }

    static List<String> zieheZufaellig(List<String> vorrat, int anzahl) {
        List<String> kopie = new ArrayList<>(vorrat);
        Collections.shuffle(kopie, ZUFALL);
        return new ArrayList<>(kopie.subList(0, Math.min(anzahl, kopie.size())));
    }

    static String wortVon(String eintrag) {
        return eintrag.split("\\|")[0];
    }

    /** Rückt den Titel so ein, dass er über den Fragen mittig steht. */
    static String zentriert(String titel) {
        int breite = 31;
        int abstand = Math.max(0, (breite - titel.length()) / 2);
        return " ".repeat(abstand) + titel;
    }

    static List<String> ladeGefragte() {
        try {
            if (Files.exists(GEDAECHTNIS)) {
                return new ArrayList<>(Files.readAllLines(GEDAECHTNIS, StandardCharsets.UTF_8));
            }
        } catch (IOException e) {
            System.out.println("Konnte gemerkte Wörter nicht lesen: " + e.getMessage());
        }
        return new ArrayList<>();
    }

    static void speichereGefragte(List<String> gefragt) {
        try {
            Files.write(GEDAECHTNIS, gefragt, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("Konnte gemerkte Wörter nicht speichern: " + e.getMessage());
            System.out.println("Der Test läuft trotzdem, merkt sich aber nichts.");
        }
    }
}
