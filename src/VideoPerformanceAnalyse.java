import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Scanner;

/**
 * Analysiert ein einzelnes eigenes Video: Warum lief es gut oder schlecht,
 * was muss beibehalten werden und was lässt sich nachjustieren, ohne das
 * Format komplett umzubauen.
 */
public class VideoPerformanceAnalyse {

    enum Bewertung {
        SCHWACH("SCHWACH"),
        DURCHSCHNITT("OK"),
        STARK("STARK");

        private final String anzeige;

        Bewertung(String anzeige) {
            this.anzeige = anzeige;
        }

        String anzeige() {
            return anzeige;
        }
    }

    /**
     * Eine gemessene Kennzahl inklusive Richtwerten und den zugehörigen Erklärungen.
     * schwachBis und starkAb sind Erfahrungswerte für Faceless-Content, keine offiziellen
     * Zahlen von TikTok - sie dienen als Orientierung, nicht als exakte Grenze.
     */
    record Kennzahl(String name, double wert, String einheit,
                    double schwachBis, double starkAb, int prioritaet,
                    String erklaerungStark, String erklaerungSchwach,
                    String massnahme, String beibehalten) {

        Bewertung bewertung() {
            if (wert < schwachBis) {
                return Bewertung.SCHWACH;
            } else if (wert >= starkAb) {
                return Bewertung.STARK;
            }
            return Bewertung.DURCHSCHNITT;
        }

        /** Wie deutlich liegt der Wert über dem Richtwert für "stark"? */
        double staerke() {
            return starkAb > 0 ? wert / starkAb : 0;
        }

        /** Wie deutlich liegt der Wert unter dem Richtwert für "schwach"? */
        double schwaeche() {
            return schwachBis > 0 ? wert / schwachBis : 1;
        }
    }

    public static void starte(Scanner scanner) {
        System.out.println("\n--- EIGENES VIDEO ANALYSIEREN ---");
        System.out.println("Die Werte findest du in der TikTok-App unter Analytics beim jeweiligen Video.\n");

        System.out.print("Kurzbeschreibung des Videos (worum ging es?): ");
        String beschreibung = scanner.nextLine().trim();
        if (beschreibung.isEmpty()) {
            beschreibung = "Unbenanntes Video";
        }

        int laenge = liesPositiveZahl(scanner, "Videolänge in Sekunden: ");
        long aufrufe = liesZahl(scanner, "Aufrufe: ", 1);
        long follower = liesZahl(scanner, "Follower zum Zeitpunkt des Posts (0 wenn unbekannt): ", 0);
        double wiedergabedauer = liesKommazahl(scanner, "Durchschnittliche Wiedergabedauer in Sekunden: ");
        long likes = liesZahl(scanner, "Likes: ", 0);
        long kommentare = liesZahl(scanner, "Kommentare: ", 0);
        long shares = liesZahl(scanner, "Geteilt (Shares): ", 0);
        long speicherungen = liesZahl(scanner, "Speicherungen (Favoriten): ", 0);
        long neueFollower = liesZahl(scanner, "Neue Follower durch dieses Video (0 wenn unbekannt): ", 0);

        List<Kennzahl> kennzahlen = baueKennzahlen(laenge, aufrufe, wiedergabedauer,
                likes, kommentare, shares, speicherungen, neueFollower);

        String bericht = erstelleBericht(beschreibung, aufrufe, follower, kennzahlen);
        System.out.println(bericht);

        System.out.print("Bericht als Textdatei speichern? (ja/nein): ");
        if (scanner.nextLine().trim().equalsIgnoreCase("ja")) {
            TikTokNischenAnalyse.speichereBericht("video_" + beschreibung, bericht);
        }
    }

    private static List<Kennzahl> baueKennzahlen(int laenge, long aufrufe, double wiedergabedauer,
                                                 long likes, long kommentare, long shares,
                                                 long speicherungen, long neueFollower) {
        double completion = wiedergabedauer / laenge * 100;
        List<Kennzahl> kennzahlen = new ArrayList<>();

        kennzahlen.add(new Kennzahl(
                "Completion-Rate (wie weit wird geschaut)",
                completion, "%", 50, 80, 1,
                "Die Zuschauer bleiben bis zum Ende. Das ist das wichtigste Einzelsignal überhaupt - " +
                        "genau deshalb hat TikTok das Video weiter ausgespielt.",
                "Die meisten steigen vorher aus. Das ist bei wenig Reichweite fast immer die eigentliche " +
                        "Ursache: Entweder greift der Hook nicht oder das Video ist länger als sein Inhalt hergibt.",
                "Kürze das Video um etwa ein Drittel und zieh die stärkste Aussage in die erste Sekunde. " +
                        "Sonst nichts ändern - Thema und Stil bleiben.",
                "Länge und Tempo genau so lassen. Diese Kombination funktioniert."
        ));

        kennzahlen.add(new Kennzahl(
                "Like-Rate",
                anteil(likes, aufrufe), "%", 4, 8, 5,
                "Das Video hat emotional getroffen. Zuschauer liken erst, wenn sie zustimmen oder " +
                        "sich wiedererkennen.",
                "Der Inhalt war verständlich, hat aber kein Gefühl ausgelöst. Meist fehlt eine klare " +
                        "Haltung oder eine Pointe am Schluss.",
                "Setz ans Ende einen Satz mit klarer Meinung statt eines neutralen Abschlusses.",
                "Den emotionalen Ton beibehalten - der trägt das Video."
        ));

        kennzahlen.add(new Kennzahl(
                "Kommentar-Rate",
                anteil(kommentare, aufrufe), "%", 0.3, 1.0, 4,
                "Das Video hat Diskussion ausgelöst. Kommentare halten die Reichweite über mehrere " +
                        "Tage am Leben, weil TikTok das Video immer wieder neu ausspielt.",
                "Niemand hatte einen konkreten Grund zu antworten. Es fehlt eine Frage, eine These " +
                        "oder ein bewusst offen gelassenes Detail.",
                "Stell am Ende eine konkrete Frage oder lass eine Sache ungeklärt, über die man " +
                        "streiten kann. Der Rest bleibt gleich.",
                "Den Auslöser für die Diskussion identifizieren und in jedem Video wiederholen."
        ));

        kennzahlen.add(new Kennzahl(
                "Share-Rate (weitergeschickt)",
                anteil(shares, aufrufe), "%", 0.3, 1.0, 2,
                "Zuschauer haben es an andere weitergeschickt. Das ist das stärkste Viral-Signal, " +
                        "weil es dem Algorithmus neue Zuschauerkreise erschließt.",
                "Unterhaltsam, aber nicht weiterschickenswert. Dafür fehlt entweder eine Überraschung " +
                        "oder ein klarer Nutzen für eine bestimmte Person.",
                "Bau einen Moment ein, bei dem man an eine konkrete Person denkt " +
                        "('schick das an jemanden, der ...'). Format sonst unverändert lassen.",
                "Genau den überraschenden Moment beibehalten, der zum Weiterschicken führt."
        ));

        kennzahlen.add(new Kennzahl(
                "Speicher-Rate",
                anteil(speicherungen, aufrufe), "%", 0.5, 2.0, 3,
                "Zuschauer wollen das Video später wiederfinden. Hoher Nutzwert - solche Videos " +
                        "werden mehrfach angesehen, was die Reichweite zusätzlich verlängert.",
                "Kein Grund zum Aufheben. Dem Video fehlt etwas, das man später nochmal braucht.",
                "Pack einen konkreten Tipp, eine Liste oder eine Anleitung dazu, ohne das Thema zu wechseln.",
                "Den Nutzwert-Teil beibehalten - der sorgt für die Speicherungen."
        ));

        kennzahlen.add(new Kennzahl(
                "Follower-Konversion",
                anteil(neueFollower, aufrufe), "%", 0.1, 0.5, 6,
                "Das Video macht neugierig auf mehr. Es zieht nicht nur Aufrufe, sondern baut " +
                        "tatsächlich den Kanal auf.",
                "Das Video hat unterhalten, aber nicht neugierig auf dein Profil gemacht. " +
                        "Reichweite ohne Follower-Wachstum verpufft.",
                "Kündige am Ende an, dass Teil 2 auf dem Profil kommt, und halte den Stil " +
                        "über alle Videos gleich, damit man dich wiedererkennt.",
                "Den Abschluss beibehalten - er wandelt Zuschauer in Follower um."
        ));

        return kennzahlen;
    }

    private static String erstelleBericht(String beschreibung, long aufrufe, long follower,
                                          List<Kennzahl> kennzahlen) {
        StringBuilder b = new StringBuilder();
        b.append("\n=================================================\n");
        b.append("Video-Analyse: ").append(beschreibung).append("\n");
        b.append("=================================================\n\n");

        b.append("--- GESAMTURTEIL ---\n\n");
        b.append(urteil(aufrufe, follower)).append("\n\n");

        b.append("--- DEINE KENNZAHLEN ---\n\n");
        for (Kennzahl k : kennzahlen) {
            b.append(String.format("[%-6s] %-42s %6.2f%s  (schwach unter %s / stark ab %s)%n",
                    k.bewertung().anzeige(), k.name(), k.wert(), k.einheit(),
                    formatiere(k.schwachBis()) + k.einheit(),
                    formatiere(k.starkAb()) + k.einheit()));
        }
        b.append("\nDie Richtwerte sind Erfahrungswerte für Faceless-Content, keine offiziellen ")
                .append("TikTok-Zahlen.\nSie zeigen die Richtung, nicht eine exakte Grenze.\n\n");

        Kennzahl treiber = staerksteKennzahl(kennzahlen);
        Kennzahl bremse = schwaechsteKennzahl(kennzahlen);

        b.append("--- WARUM DAS VIDEO SO GELAUFEN IST ---\n\n");
        if (treiber != null) {
            b.append("Das hat es getragen - ").append(treiber.name()).append(":\n");
            b.append(treiber.erklaerungStark()).append("\n\n");
        }
        if (bremse != null) {
            b.append("Das hat es ausgebremst - ").append(bremse.name()).append(":\n");
            b.append(bremse.erklaerungSchwach()).append("\n\n");
        }
        if (treiber == null && bremse == null) {
            b.append("Alle Werte liegen im mittleren Bereich. Das Video ist weder durch eine Stärke\n");
            b.append("herausgestochen noch durch eine Schwäche eingebrochen - solche Videos laufen\n");
            b.append("solide, aber unauffällig. Um auszubrechen, brauchst du einen bewusst\n");
            b.append("zugespitzten Punkt: eine klare Meinung, eine Frage oder eine Überraschung.\n\n");
        }

        List<Kennzahl> starke = kennzahlen.stream().filter(k -> k.bewertung() == Bewertung.STARK).toList();
        if (!starke.isEmpty()) {
            b.append("--- DAS UNBEDINGT BEIBEHALTEN ---\n\n");
            int i = 1;
            for (Kennzahl k : starke) {
                b.append(i++).append(". ").append(k.beibehalten()).append("\n");
            }
            b.append("\n");
        }

        List<Kennzahl> schwache = kennzahlen.stream()
                .filter(k -> k.bewertung() == Bewertung.SCHWACH)
                .sorted(schwachstellenReihenfolge())
                .toList();
        b.append("--- FEINJUSTIERUNG (ohne das Format zu ändern) ---\n\n");
        if (schwache.isEmpty()) {
            b.append("Es gibt keine klare Schwachstelle. Ändere jetzt bewusst nichts am Format,\n");
            b.append("sondern wiederhole es und teste nur eine Sache pro Video (z.B. nur den Hook),\n");
            b.append("damit du weißt, worauf eine Veränderung zurückgeht.\n\n");
        } else {
            int i = 1;
            for (Kennzahl k : schwache) {
                b.append(i++).append(". ").append(k.massnahme()).append("\n");
            }
            b.append("\nDie Punkte stehen in der Reihenfolge ihrer Wirkung - fang mit Punkt 1 an.\n");
            b.append("Ändere pro Video nur einen davon. Änderst du alles gleichzeitig, weißt du\n");
            b.append("am Ende nicht, was gewirkt hat.\n\n");
        }

        b.append("--- NÄCHSTER SCHRITT ---\n\n");
        b.append(naechsterSchritt(aufrufe, follower, treiber, bremse)).append("\n");

        return b.toString();
    }

    private static String urteil(long aufrufe, long follower) {
        if (follower <= 0) {
            return "Aufrufe: " + aufrufe + " (ohne Followerzahl ist keine Einordnung möglich - "
                    + "entscheidend ist nicht die absolute Zahl,\nsondern das Verhältnis von Aufrufen zu Followern).";
        }

        double faktor = (double) aufrufe / follower;
        String basis = String.format("Aufrufe: %d bei %d Followern - das entspricht dem %.1f-fachen "
                + "deiner Followerzahl.%n%n", aufrufe, follower, faktor);

        if (faktor >= 20) {
            return basis + "Das ist viral. Der Großteil der Aufrufe kam von Leuten, die dir nicht folgen - "
                    + "TikTok hat das Video\nbreit auf der For-You-Page ausgespielt. Dieses genaue Muster "
                    + "(Hook, Länge, Aufbau) solltest du jetzt\nmehrfach wiederholen, solange es läuft.";
        } else if (faktor >= 5) {
            return basis + "Das ist deutlich über dem Normalfall. Die For-You-Page hat das Video gepusht, "
                    + "es ist aber noch nicht\ndurchgestartet. Meist fehlt genau ein Signal - siehe unten, "
                    + "welches das bei dir ist.";
        } else if (faktor >= 1) {
            return basis + "Das ist der Normalbereich: Das Video hat vor allem deine eigene Zielgruppe "
                    + "erreicht, aber kaum neue\nZuschauer. Für Wachstum brauchst du ein Signal, das "
                    + "TikTok überzeugt, breiter auszuspielen.";
        }
        return basis + "Das Video hat nicht einmal deine eigenen Follower erreicht. Das passiert, wenn "
                + "die ersten Zuschauer\nfrüh abspringen: TikTok testet jedes Video zuerst bei einer "
                + "kleinen Gruppe und stoppt die Ausspielung,\nwenn dort die Reaktion ausbleibt.";
    }

    private static String naechsterSchritt(long aufrufe, long follower, Kennzahl treiber, Kennzahl bremse) {
        double faktor = follower > 0 ? (double) aufrufe / follower : 0;

        if (faktor >= 5 && treiber != null) {
            return "Bau die nächsten 3-5 Videos nach exakt demselben Muster - gleiche Länge, gleicher "
                    + "Aufbau, nur anderes Thema.\nSolange ein Format läuft, ist Wiederholung wertvoller "
                    + "als eine neue Idee. Erst wenn die Aufrufe zwei- bis dreimal\nhintereinander "
                    + "einbrechen, änderst du etwas.";
        }
        if (bremse != null) {
            return "Poste das nächste Video mit genau einer Änderung: " + bremse.massnahme()
                    + "\nAlles andere bleibt gleich. Danach vergleichst du beide Videos in dieser Analyse "
                    + "und siehst schwarz auf weiß,\nob die Änderung gewirkt hat.";
        }
        return "Wiederhole das Format 3-5 Mal und analysiere jedes Video hier. Erst über mehrere Videos "
                + "hinweg erkennst du,\nwas Zufall war und was wirklich an deinem Format liegt.";
    }

    private static Kennzahl staerksteKennzahl(List<Kennzahl> kennzahlen) {
        return kennzahlen.stream()
                .filter(k -> k.bewertung() == Bewertung.STARK)
                .max((a, c) -> Double.compare(a.staerke(), c.staerke()))
                .orElse(null);
    }

    /**
     * Die Bremse ist nicht einfach der niedrigste Wert, sondern die ursächlichste Schwäche:
     * Wird ein Video kaum zu Ende geschaut, sind fehlende Kommentare oder Shares nur die Folge
     * davon. Deshalb entscheidet zuerst die Priorität und erst danach der Abstand zum Richtwert.
     */
    private static Kennzahl schwaechsteKennzahl(List<Kennzahl> kennzahlen) {
        return kennzahlen.stream()
                .filter(k -> k.bewertung() == Bewertung.SCHWACH)
                .min(schwachstellenReihenfolge())
                .orElse(null);
    }

    private static Comparator<Kennzahl> schwachstellenReihenfolge() {
        return Comparator.comparingInt(Kennzahl::prioritaet)
                .thenComparingDouble(Kennzahl::schwaeche);
    }

    private static double anteil(long teil, long gesamt) {
        return gesamt > 0 ? (double) teil / gesamt * 100 : 0;
    }

    private static String formatiere(double wert) {
        return wert == Math.floor(wert) ? String.valueOf((int) wert) : String.valueOf(wert);
    }

    private static int liesPositiveZahl(Scanner scanner, String prompt) {
        while (true) {
            System.out.print(prompt);
            try {
                int wert = Integer.parseInt(scanner.nextLine().trim());
                if (wert > 0) {
                    return wert;
                }
                System.out.println("Bitte eine Zahl größer als 0 eingeben.");
            } catch (NumberFormatException e) {
                System.out.println("Bitte eine ganze Zahl eingeben.");
            }
        }
    }

    private static long liesZahl(Scanner scanner, String prompt, long minimum) {
        while (true) {
            System.out.print(prompt);
            try {
                long wert = Long.parseLong(scanner.nextLine().trim());
                if (wert >= minimum) {
                    return wert;
                }
                System.out.println("Bitte mindestens " + minimum + " eingeben.");
            } catch (NumberFormatException e) {
                System.out.println("Bitte eine ganze Zahl eingeben.");
            }
        }
    }

    private static double liesKommazahl(Scanner scanner, String prompt) {
        while (true) {
            System.out.print(prompt);
            try {
                double wert = Double.parseDouble(scanner.nextLine().trim().replace(',', '.'));
                if (wert >= 0) {
                    return wert;
                }
                System.out.println("Bitte eine Zahl ab 0 eingeben.");
            } catch (NumberFormatException e) {
                System.out.println("Bitte eine Zahl eingeben (z.B. 12.5).");
            }
        }
    }
}
