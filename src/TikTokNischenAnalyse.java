import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.Scanner;

public class TikTokNischenAnalyse {

    record Nische(String name, List<String> keywords, String warumEsFunktioniert,
                   String hookFormel, List<String> twistIdeen, List<String> schritte) {
    }

    private static final Nische ALLGEMEIN = new Nische(
            "Allgemeiner Faceless-Content (Nische nicht eindeutig erkannt)",
            List.of(),
            "Ohne klare Nische verteilt sich deine Zielgruppe - der Algorithmus kann dich schwerer " +
                    "wiederkehrenden Zuschauern zuordnen. Erfolgreiche Faceless-Kanäle bedienen fast immer " +
                    "ein sehr enges, wiedererkennbares Thema.",
            "'[Überraschende Aussage] - und das ist erst der Anfang.'",
            List.of(
                    "Grenze dein Thema enger ein, bis du es in einem Satz beschreiben kannst ('Fakten nur über das Weltall')",
                    "Schau dir 5-10 Videos des Kanals genau an und notiere, was sich in JEDEM Video wiederholt (Struktur, Musik, Overlay)",
                    "Kopiere die Struktur, aber wechsle das Thema in eine Nische, die du selbst gut kennst"
            ),
            List.of(
                    "Beschreibe den Kanal beim nächsten Mal genauer (Thema, Format, Stil), damit eine passende Nische erkannt werden kann",
                    "Skript schreiben (kostenlos: ChatGPT Free, Notiz-App)",
                    "Kostenlose Stimme nutzen (CapCut Text-to-Speech oder Google Text-to-Speech)",
                    "Gratis-Footage von Pexels.com oder Pixabay.com verwenden",
                    "Mit CapCut (kostenlos) schneiden und automatische Untertitel erzeugen lassen",
                    "Aktuellen Trend-Sound aus der TikTok-App wählen und täglich posten"
            )
    );

    private static final List<Nische> NISCHEN = List.of(
            new Nische(
                    "Fakten & Wissen",
                    List.of("fakten", "wusstest du", "wissen", "trivia", "interessant", "did you know"),
                    "Kurze, überraschende Wissenshäppchen erzeugen einen 'Ich muss das weitererzählen'-Reflex " +
                            "und werden deshalb überdurchschnittlich oft geteilt.",
                    "'Die meisten Menschen wissen das nicht: ...' oder '3 Fakten, die dein Weltbild verändern'",
                    List.of(
                            "Statt allgemeiner Fakten: Fakten aus EINER sehr engen Nische (nur Gehirn, nur Weltraum, nur Geld)",
                            "Fakten im 'Mythos vs. Wahrheit'-Format erzählen statt neutral aufzuzählen",
                            "Fakten mit kurzer eigener Reaktion/Meinung verbinden statt sie nur vorzulesen"
                    ),
                    List.of(
                            "Enges Thema festlegen, nicht 'alles Mögliche'",
                            "Skript mit 3-5 Fakten und starkem Hook-Satz schreiben (kostenlos: ChatGPT Free)",
                            "Kostenlose TTS-Stimme nutzen (CapCut Text-to-Speech, Google Text-to-Speech)",
                            "Passende Gratis-Clips bei Pexels.com oder Pixabay.com laden",
                            "In CapCut (kostenlos) schneiden, Text-Overlay pro Fakt einblenden",
                            "Automatische Untertitel per CapCut Auto-Captions erzeugen",
                            "Aktuellen Trend-Sound aus der TikTok-App auswählen",
                            "Zu Zeiten mit hoher Aktivität deiner Zielgruppe posten (z.B. 18-21 Uhr) und testen"
                    )
            ),
            new Nische(
                    "Motivation & Mindset",
                    List.of("motivation", "zitat", "quote", "mindset", "erfolg", "disziplin"),
                    "Cinematische Bilder plus eine tiefe Stimme mit starken Aussagen erzeugen ein Gefühl von " +
                            "Ansporn - Zuschauer speichern solche Videos, um sie später wieder anzusehen.",
                    "'Niemand wird dich retten. Hier ist, was du stattdessen tun musst.'",
                    List.of(
                            "Motivation für eine sehr konkrete Zielgruppe statt allgemein (z.B. nur für Gym-Anfänger, nur für Gründer)",
                            "Eigene kurze Geschichte/Erfahrung statt fremder Zitate verwenden",
                            "Motivation mit einem klaren 3-Schritte-Tipp am Ende statt nur Gefühl"
                    ),
                    List.of(
                            "Zielgruppe genau definieren (wer genau soll sich angesprochen fühlen)",
                            "Kurzes Skript mit starkem ersten Satz schreiben",
                            "Kostenlose tiefe TTS-Stimme wählen (CapCut TTS, ElevenLabs Free-Kontingent)",
                            "Cinematische Gratis-Clips bei Pexels.com oder Mixkit.co laden",
                            "In CapCut schneiden, langsame Zooms/Übergänge nutzen",
                            "Text-Overlay der Kernsätze einblenden, automatische Untertitel aktivieren",
                            "Ruhigen, cinematischen Trend-Sound wählen und regelmäßig posten"
                    )
            ),
            new Nische(
                    "Reddit-Storytime (vorgelesene Geschichten)",
                    List.of("reddit", "aita", "storytime", "vorgelesen", "text to speech", "geschichte vorgelesen"),
                    "Echte, emotionale Alltagsgeschichten machen neugierig auf den Ausgang - kombiniert mit " +
                            "belanglosem Gameplay im Hintergrund (z.B. Subway Surfers) hält das die Watchtime hoch, " +
                            "weil das Gehirn beide Reize gleichzeitig verarbeiten will.",
                    "'Ich habe meiner besten Freundin die Hochzeit ruiniert - und ich würde es wieder tun.'",
                    List.of(
                            "Eigene, spezifische Story-Kategorie wählen statt gemischter Themen (z.B. nur Arbeit/Chef-Storys)",
                            "Geschichten in Cliffhanger-Teilen als Serie posten (Teil 1, Teil 2 ...)",
                            "Community eigene Geschichten einsenden lassen, statt nur Reddit zu nutzen"
                    ),
                    List.of(
                            "Passende Geschichte auf Reddit suchen (z.B. r/AmItheAsshole, r/relationship_advice) - Regeln des Subreddits beachten",
                            "Text kürzen/anpassen, damit er in 30-90 Sekunden passt",
                            "Kostenlose TTS-Stimme erzeugen (CapCut TTS oder Google Text-to-Speech)",
                            "Gratis-Hintergrundgameplay (z.B. Parkour/Subway-Surfers-Clips) besorgen, das rechtefrei nutzbar ist",
                            "In CapCut Story-Audio über das Hintergrundvideo legen",
                            "Automatische Untertitel aktivieren (erhöht Watchtime deutlich)",
                            "Am Ende bewusst einen Cliffhanger setzen, um Teil 2 anzukündigen"
                    )
            ),
            new Nische(
                    "Psychologie-Tricks",
                    List.of("psychologie", "psychology", "manipulation", "körpersprache", "dark psychology"),
                    "Wissen über 'wie Menschen ticken' fühlt sich wie ein Vorteil im Alltag an - das macht diese " +
                            "Videos besonders speicherwürdig und teilenswert.",
                    "'Dieser Trick lässt jeden Menschen dir sofort vertrauen.'",
                    List.of(
                            "Psychologie-Tricks nur für einen Lebensbereich (Dating, Beruf, Verhandlung) statt gemischt",
                            "Jeden Trick mit einem kurzen Beispiel-Dialog demonstrieren statt nur zu erklären",
                            "Serie 'Trick der Woche' mit wiedererkennbarem Intro aufbauen"
                    ),
                    List.of(
                            "Seriöse Quelle für den Trick suchen (Bücher, Studien) - keine erfundenen Behauptungen",
                            "Kurzes Skript mit Trick + Beispiel schreiben",
                            "Kostenlose TTS-Stimme oder eigene Stimme (auch ohne Gesicht möglich) aufnehmen",
                            "Gratis B-Roll (Gespräche, Business, Alltag) bei Pexels.com laden",
                            "In CapCut schneiden, Kernsatz als Text-Overlay hervorheben",
                            "Automatische Untertitel aktivieren und mit Trend-Sound kombinieren"
                    )
            ),
            new Nische(
                    "Luxus & Wealth",
                    List.of("luxus", "reich", "geld", "wealth", "money", "lifestyle"),
                    "Aufnahmen von Reichtum lösen Neugier und Zukunftsträume aus - Zuschauer schauen sich das " +
                            "'Leben, das sie wollen' an, auch ohne Gesicht des Erstellers.",
                    "'So sieht ein Tag als Millionär wirklich aus.'",
                    List.of(
                            "Statt reinem Lifestyle: 'Wie man dorthin kommt' - konkrete Geld-Tipps statt nur Bilder",
                            "Vergleichs-Format nutzen: 'Broke vs. Reich'-Gegenüberstellungen",
                            "Eigene, glaubwürdige Nische wählen (z.B. Investieren für Anfänger statt reiner Protzerei)"
                    ),
                    List.of(
                            "Konkreten Unter-Winkel wählen (Investieren, Sparen, Business statt nur 'Luxus zeigen')",
                            "Skript mit Hook + 1 nützlichem Gedanken schreiben",
                            "Gratis Luxus-B-Roll bei Pexels.com/Pixabay.com suchen (Autos, Städte, Business)",
                            "Kostenlose TTS-Stimme oder eigene Stimme nutzen",
                            "In CapCut schneiden, dynamische Schnitte im Sekundentakt",
                            "Automatische Untertitel + aktuellen Trend-Sound verwenden"
                    )
            ),
            new Nische(
                    "Geschichte & History-Facts",
                    List.of("history", "historisch", "weltkrieg", "antike", "mittelalter", "geschichte der"),
                    "Dramatische, wenig bekannte historische Momente wirken wie 'verbotenes Wissen' und werden " +
                            "deshalb gern in Gruppenchats geteilt.",
                    "'Das ist das dunkelste Kapitel, über das in der Schule nie gesprochen wird.'",
                    List.of(
                            "Eine enge Epoche/Region wählen statt 'random Geschichte' (z.B. nur Antikes Rom)",
                            "Geschichten als 'Was wäre, wenn'-Szenario erzählen statt reiner Fakten",
                            "Serie mit durchlaufender Chronologie aufbauen (z.B. jede Woche 1 Jahrzehnt)"
                    ),
                    List.of(
                            "Verlässliche Quelle recherchieren (Bücher, Dokumentationen, seriöse Wikipedia-Quellen)",
                            "Kurzes, spannend geschriebenes Skript mit Hook erstellen",
                            "Kostenlose TTS-Stimme mit dramatischem Ton wählen",
                            "Gratis historisches B-Roll/Bilder (gemeinfrei, z.B. Wikimedia Commons, Pexels) nutzen",
                            "In CapCut mit Ken-Burns-Effekt (langsames Zoomen auf Bilder) schneiden",
                            "Automatische Untertitel aktivieren und passenden dramatischen Trend-Sound wählen"
                    )
            ),
            new Nische(
                    "Top-Listen & Rankings",
                    List.of("top 5", "top 10", "liste", "ranking", "die besten", "top10", "top5"),
                    "Listen geben dem Gehirn eine klare Struktur und einen Grund, bis zum Ende zu schauen " +
                            "('Was ist Platz 1?') - das treibt die Watchtime nach oben.",
                    "'Platz 5 wird dich überraschen - aber Platz 1 ist unfassbar.'",
                    List.of(
                            "Extrem enges Listenthema wählen (nicht 'Top 10 Autos', sondern 'Top 5 Autos unter 10.000€')",
                            "Ranking mit eigener Begründung/Bewertung versehen statt nur aufzuzählen",
                            "Zuschauer im Kommentar über Platz 1 abstimmen lassen, bevor er in Teil 2 aufgelöst wird"
                    ),
                    List.of(
                            "Enges Listenthema und Kriterium für das Ranking festlegen",
                            "Skript mit Countdown-Struktur (Platz 5 bis Platz 1) schreiben",
                            "Kostenlose TTS-Stimme oder eigene Stimme aufnehmen",
                            "Passende Gratis-Clips/Bilder pro Listenpunkt bei Pexels.com/Pixabay.com sammeln",
                            "In CapCut schneiden, Platzierungs-Zahl groß als Overlay einblenden",
                            "Automatische Untertitel aktivieren und Spannungs-Sound für Platz 1 nutzen"
                    )
            ),
            new Nische(
                    "ASMR & Satisfying",
                    List.of("asmr", "satisfying", "entspannend", "seife schneiden", "kinetic sand", "oddly satisfying"),
                    "Repetitive, saubere Bewegungen und Sounds lösen ein beruhigendes Gefühl aus - Zuschauer " +
                            "schauen oft passiv sehr lange zu, was die Watchtime stark erhöht.",
                    "Kein gesprochener Hook nötig - der erste visuelle Reiz in Sekunde 1 muss sofort 'satisfying' wirken",
                    List.of(
                            "Eigenes, noch seltenes Material finden statt bekannte ASMR-Trends zu kopieren",
                            "Serie mit wiedererkehrendem Objekt/Material aufbauen (Wiedererkennungswert)",
                            "Leichten Lern-Effekt einbauen (z.B. 'so wird X hergestellt') statt nur reinem Sound"
                    ),
                    List.of(
                            "Ruhige Umgebung und gutes Mikrofon (auch Handy-Mikro reicht oft) für sauberen Ton nutzen",
                            "Motiv/Material auswählen, das noch nicht überall zu sehen ist",
                            "In gleichmäßigem Tempo und naher Kameraeinstellung filmen (Handy reicht)",
                            "In CapCut nur minimal schneiden, Ton-Qualität priorisieren, Video nicht überladen",
                            "Kein Overlay-Text nötig, ggf. kurzer Titel am Anfang",
                            "Ruhigen oder passenden Trend-Sound leise unterlegen und regelmäßig posten"
                    )
            ),
            new Nische(
                    "Horror & Gruselgeschichten",
                    List.of("horror", "gruselgeschichte", "creepy", "scary story", "gruselig"),
                    "Angst ist ein extrem starker, körperlicher Trigger - Zuschauer schauen aus Nervenkitzel bis " +
                            "zum Ende und kommentieren häufig, was den Algorithmus zusätzlich pusht.",
                    "'Das ist mir wirklich passiert - und ich schlafe seitdem mit Licht.'",
                    List.of(
                            "Enges Grusel-Sub-Genre wählen (z.B. nur wahre Begebenheiten, nur Wald/Camping-Storys)",
                            "Geschichten als mehrteilige Serie mit Cliffhanger erzählen",
                            "Zuschauer eigene Grusel-Erlebnisse einsenden lassen für authentischen Content"
                    ),
                    List.of(
                            "Kurze, spannend aufgebaute Gruselgeschichte schreiben oder recherchieren (z.B. r/nosleep, kostenlos nutzbar mit Quellenangabe/Erlaubnis)",
                            "Kostenlose dunkle/tiefe TTS-Stimme nutzen (CapCut TTS)",
                            "Dunkles, ruhiges Gratis-B-Roll (Wald, leere Straßen, Nebel) bei Pexels.com laden",
                            "In CapCut mit dunklem Filter und langsamen Schnitten arbeiten",
                            "Automatische Untertitel aktivieren, an Spannungspunkten kurz Stille/Soundeffekt setzen",
                            "Am Ende bewusst offenes Ende/Cliffhanger für Teil 2 lassen"
                    )
            )
    );

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8);

        System.out.println("=================================================");
        System.out.println("   TikTok Faceless-Nischenanalyse (kostenlos)");
        System.out.println("=================================================");
        System.out.println("Beschreibe einen TikTok-Kanal - du bekommst eine Nischenanalyse,");
        System.out.println("eine eigene Twist-Idee und eine Schritt-für-Schritt-Anleitung");
        System.out.println("zum kostenlosen Nachbauen.");
        System.out.println();

        boolean weiter = true;
        while (weiter) {
            analysiereKanal(scanner);
            System.out.print("\nNoch einen Kanal analysieren? (ja/nein): ");
            weiter = scanner.nextLine().trim().equalsIgnoreCase("ja");
            System.out.println();
        }

        System.out.println("Viel Erfolg beim Nachbauen deiner eigenen Version!");
        scanner.close();
    }

    private static void analysiereKanal(Scanner scanner) {
        System.out.print("Kanalname (optional, Enter zum Überspringen): ");
        String kanalname = scanner.nextLine().trim();
        if (kanalname.isEmpty()) {
            kanalname = "Unbenannter Kanal";
        }

        System.out.print("Worum geht es im Content? (Thema, Format, Stil in ein paar Worten): ");
        String beschreibung = scanner.nextLine().trim();

        System.out.print("Wie beginnt ein typisches Video (Hook, erste 1-3 Sekunden)? ");
        String hook = scanner.nextLine().trim();

        int videoLaenge = liesInt(scanner, "Durchschnittliche Videolänge in Sekunden: ");
        int postingsProWoche = liesInt(scanner, "Wie oft postet der Kanal pro Woche? ");
        long durchschnittsViews = liesLong(scanner, "Durchschnittliche Views (0 wenn unbekannt): ");

        Nische erkannteNische = erkenneNische(beschreibung + " " + hook);

        String bericht = erstelleBericht(kanalname, videoLaenge, postingsProWoche, durchschnittsViews, erkannteNische);
        System.out.println(bericht);

        System.out.print("Bericht als Textdatei speichern? (ja/nein): ");
        if (scanner.nextLine().trim().equalsIgnoreCase("ja")) {
            speichereBericht(kanalname, bericht);
        }
    }

    private static Nische erkenneNische(String eingabeText) {
        String text = eingabeText.toLowerCase(Locale.GERMAN);
        Nische bestenTreffer = ALLGEMEIN;
        int besterScore = 0;

        for (Nische nische : NISCHEN) {
            int score = 0;
            for (String keyword : nische.keywords()) {
                if (text.contains(keyword)) {
                    score++;
                }
            }
            if (score > besterScore) {
                besterScore = score;
                bestenTreffer = nische;
            }
        }
        return bestenTreffer;
    }

    private static String erstelleBericht(String kanalname, int videoLaenge, int postingsProWoche,
                                           long durchschnittsViews, Nische nische) {
        StringBuilder bericht = new StringBuilder();
        bericht.append("\n=================================================\n");
        bericht.append("Nischenanalyse: ").append(kanalname).append("\n");
        bericht.append("=================================================\n\n");

        bericht.append("Erkannte Nische: ").append(nische.name()).append("\n\n");
        bericht.append("Warum der Content funktioniert:\n").append(nische.warumEsFunktioniert()).append("\n\n");
        bericht.append("Typische Hook-Formel:\n").append(nische.hookFormel()).append("\n\n");

        bericht.append("Einschätzung deiner Kennzahlen:\n");
        bericht.append("- Videolänge (").append(videoLaenge).append("s): ")
                .append(bewerteVideolaenge(videoLaenge)).append("\n");
        bericht.append("- Postings pro Woche (").append(postingsProWoche).append("): ")
                .append(bewertePostingFrequenz(postingsProWoche)).append("\n");
        bericht.append("- Durchschnittliche Views: ").append(bewerteViews(durchschnittsViews)).append("\n\n");

        bericht.append("Twist-Ideen (gleiche Erfolgsformel, eigener Winkel):\n");
        int i = 1;
        for (String twist : nische.twistIdeen()) {
            bericht.append(i++).append(". ").append(twist).append("\n");
        }
        bericht.append("\n");

        bericht.append("Schritt-für-Schritt-Nachbau (so gut wie kostenlos):\n");
        int j = 1;
        for (String schritt : nische.schritte()) {
            bericht.append(j++).append(". ").append(schritt).append("\n");
        }

        return bericht.toString();
    }

    private static String bewerteVideolaenge(int sekunden) {
        if (sekunden <= 0) {
            return "keine Angabe";
        } else if (sekunden < 15) {
            return "sehr kurz - funktioniert nur, wenn der Hook allein schon den ganzen Inhalt trägt";
        } else if (sekunden <= 60) {
            return "guter Bereich für hohe Completion-Rate auf TikTok";
        } else {
            return "eher lang - nur sinnvoll, wenn Cliffhanger/Spannung den Zuschauer bis zum Ende halten";
        }
    }

    private static String bewertePostingFrequenz(int proWoche) {
        if (proWoche <= 0) {
            return "keine Angabe";
        } else if (proWoche < 3) {
            return "unter dem Wachstums-Minimum - in der Startphase gelten 1x täglich (7x/Woche) als Richtwert";
        } else if (proWoche < 7) {
            return "solide, aber tägliches Posten beschleunigt das Wachstum meist deutlich";
        } else {
            return "starke Frequenz - das begünstigt den Algorithmus in der Wachstumsphase";
        }
    }

    private static String bewerteViews(long views) {
        if (views <= 0) {
            return "keine Angabe";
        } else if (views < 1_000) {
            return views + " - Testphase, Format/Hook noch optimieren";
        } else if (views < 10_000) {
            return views + " - erste Traktion, konsequent an Hook und Thema festhalten";
        } else if (views < 100_000) {
            return views + " - solide Performance, dieses Format lohnt sich zu skalieren";
        } else {
            return views + " - viral, dieses genaue Muster (Hook, Format, Länge) unbedingt wiederholen";
        }
    }

    private static void speichereBericht(String kanalname, String bericht) {
        try {
            Path ordner = Path.of("berichte");
            Files.createDirectories(ordner);

            String zeitstempel = DateTimeFormatter.ofPattern("yyyy-MM-dd_HHmmss").format(LocalDateTime.now());
            String dateiname = säubereDateiname(kanalname) + "_" + zeitstempel + ".txt";
            Path datei = ordner.resolve(dateiname);

            Files.writeString(datei, bericht, StandardCharsets.UTF_8);
            System.out.println("Gespeichert unter: " + datei.toAbsolutePath());
        } catch (IOException e) {
            System.out.println("Konnte Bericht nicht speichern: " + e.getMessage());
        }
    }

    private static String säubereDateiname(String name) {
        String bereinigt = name.replaceAll("[^a-zA-Z0-9äöüÄÖÜß_-]", "_");
        return bereinigt.isBlank() ? "kanal" : bereinigt;
    }

    private static int liesInt(Scanner scanner, String prompt) {
        while (true) {
            System.out.print(prompt);
            String eingabe = scanner.nextLine().trim();
            try {
                return Integer.parseInt(eingabe);
            } catch (NumberFormatException e) {
                System.out.println("Bitte eine ganze Zahl eingeben.");
            }
        }
    }

    private static long liesLong(Scanner scanner, String prompt) {
        while (true) {
            System.out.print(prompt);
            String eingabe = scanner.nextLine().trim();
            try {
                return Long.parseLong(eingabe);
            } catch (NumberFormatException e) {
                System.out.println("Bitte eine ganze Zahl eingeben.");
            }
        }
    }
}
