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

    /** Einfachere Nische mit ähnlichem oder besserem Potenzial. */
    record Alternative(String name, String warumGenausoGut, String warumEinfacher,
                       int aufwandMinuten, List<String> schnellstart) {
    }

    record Nische(String name, List<String> keywords,
                  String psychologie, String algorithmus,
                  String hookFormel, int aufwandMinuten,
                  List<String> besserMachen, List<String> twistIdeen,
                  List<String> schritte, Alternative alternative) {
    }

    private static final Nische ALLGEMEIN = new Nische(
            "Allgemeiner Faceless-Content (Nische nicht eindeutig erkannt)",
            List.of(),
            "Ohne klares Thema weiß der Zuschauer nach 2 Sekunden nicht, was ihn erwartet - und wischt weiter. " +
                    "Wiedererkennbarkeit ist der Grund, warum Zuschauer beim zweiten Video hängen bleiben.",
            "Der Algorithmus baut sich ein Profil davon, WEM er deinen Kanal zeigt. Springst du zwischen Themen, " +
                    "wird dieses Profil bei jedem Video zurückgesetzt und du startest jedes Mal bei null.",
            "'[Überraschende Aussage] - und das ist erst der Anfang.'",
            25,
            List.of(
                    "Formuliere deine Nische in einem Satz ('Fakten nur über das Weltall') - schaffst du das nicht, ist sie zu breit",
                    "Schau 10 Videos des Kanals an und notiere, was sich in JEDEM wiederholt - genau das ist die Formel",
                    "Halte Format, Länge und Stil 30 Videos lang konstant, bevor du etwas änderst"
            ),
            List.of(
                    "Grenze das Thema ein, bis es in einen Satz passt",
                    "Übernimm die Struktur des Kanals, aber wechsle in ein Thema, das du selbst gut kennst",
                    "Baue ein wiedererkennbares Element ein (gleiche Stimme, gleicher Intro-Satz, gleiche Farbe)"
            ),
            List.of(
                    "Beschreibe den Kanal beim nächsten Durchlauf genauer (Thema, Format, Stil) für eine passende Nische",
                    "Skript schreiben (kostenlos: Notiz-App, ChatGPT Free)",
                    "Kostenlose Stimme nutzen (CapCut Text-to-Speech oder Google Text-to-Speech)",
                    "Gratis-Footage von Pexels.com oder Pixabay.com verwenden",
                    "Mit CapCut (kostenlos) schneiden und automatische Untertitel erzeugen lassen",
                    "Aktuellen Trend-Sound aus der TikTok-App wählen und täglich posten"
            ),
            new Alternative(
                    "Ein-Tipp-Videos aus deinem eigenen Interessengebiet",
                    "Ein einzelner nützlicher Tipp pro Video wird stark gespeichert - Speicherungen zählen für den " +
                            "Algorithmus mehr als Likes.",
                    "Du recherchierst nichts, was du nicht ohnehin weißt. Ein Clip, ein Satz, fertig.",
                    10,
                    List.of(
                            "Schreibe 20 Tipps aus deinem Hobby/Job auf eine Liste - das ist dein Content für 20 Videos",
                            "Pro Video: 1 Tipp, 15-20 Sekunden, 1 Gratis-Clip von Pexels.com",
                            "CapCut: Text-Overlay + Auto-Untertitel + Trend-Sound, fertig"
                    )
            )
    );

    private static final List<Nische> NISCHEN = List.of(
            new Nische(
                    "Fakten & Wissen",
                    List.of("fakten", "wusstest du", "wissen", "trivia", "interessant", "did you know"),
                    "Überraschendes Wissen erzeugt einen 'das muss ich weitererzählen'-Reflex. Der Zuschauer bekommt " +
                            "in 20 Sekunden das Gefühl, klüger geworden zu sein - das ist eine sehr günstige Belohnung.",
                    "Solche Videos werden überdurchschnittlich oft geteilt und in Kommentaren diskutiert " +
                            "('das stimmt nicht!'). Shares und Kommentare sind die stärksten Signale für den Algorithmus.",
                    "'Die meisten Menschen wissen das nicht: ...' oder '3 Fakten, die dein Weltbild verändern'",
                    30,
                    List.of(
                            "Nimm die Fakten mit der höchsten Kommentarzahl beim Vorbild und mach daraus ein eigenes, tieferes Video",
                            "Baue absichtlich einen leicht widersprüchlichen Fakt ein - Widerspruch in den Kommentaren pusht die Reichweite",
                            "Setze den stärksten Fakt an den Anfang, nicht ans Ende (viele Kanäle machen das falsch und verlieren früh Zuschauer)",
                            "Nenne kurz die Quelle im Overlay - das hebt dich von den meisten Fakten-Kanälen ab und wirkt seriöser"
                    ),
                    List.of(
                            "Statt allgemeiner Fakten: Fakten aus EINER engen Nische (nur Gehirn, nur Weltraum, nur Geld)",
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
                    ),
                    new Alternative(
                            "Ein-Fakt-Videos (1 Fakt = 1 Video, 15 Sekunden)",
                            "Kürzere Videos werden häufiger komplett angesehen. Eine hohe Completion-Rate ist das " +
                                    "wichtigste Einzelsignal für Reichweite - kurze Ein-Fakt-Videos gewinnen hier fast immer.",
                            "Du brauchst pro Video nur einen Fakt und einen einzigen Clip statt fünf. Aus einer " +
                                    "Recherche-Session von 30 Minuten holst du 10 fertige Videos statt zwei.",
                            12,
                            List.of(
                                    "Sammle in einer Sitzung 10 Fakten zu deinem Thema in einer Notiz",
                                    "Pro Fakt: 1 Gratis-Clip von Pexels.com + 1 Satz TTS in CapCut",
                                    "Alle 10 Videos am Stück bauen und über die Woche verteilt posten"
                            )
                    )
            ),
            new Nische(
                    "Motivation & Mindset",
                    List.of("motivation", "zitat", "quote", "mindset", "erfolg", "disziplin"),
                    "Cinematische Bilder plus tiefe Stimme erzeugen ein kurzes Hochgefühl. Der Zuschauer speichert " +
                            "das Video, weil er dieses Gefühl später wieder abrufen will.",
                    "Motivations-Content wird extrem oft gespeichert und erneut angesehen. Wiederholtes Ansehen " +
                            "desselben Videos ist ein starkes Qualitätssignal für den Algorithmus.",
                    "'Niemand wird dich retten. Hier ist, was du stattdessen tun musst.'",
                    25,
                    List.of(
                            "Werde konkreter als das Vorbild: Statt 'gib niemals auf' ein klarer Schritt, den man heute umsetzen kann",
                            "Sprich EINE Zielgruppe direkt an ('wenn du 19 bist und keinen Plan hast') statt alle - direkte Ansprache stoppt das Wischen",
                            "Halte Musik, Stimme und Schriftart über alle Videos identisch - Wiedererkennung baut Stammzuschauer auf",
                            "Ende mit einer Frage statt einem Zitat - das erzeugt Kommentare, die reine Zitat-Videos nicht bekommen"
                    ),
                    List.of(
                            "Motivation für eine sehr konkrete Zielgruppe statt allgemein (nur Gym-Anfänger, nur Gründer)",
                            "Eigene kurze Erfahrung statt fremder Zitate verwenden",
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
                    ),
                    new Alternative(
                            "Zitat-Loops (ein Satz auf einem loopenden Clip, ganz ohne Stimme)",
                            "Ohne Sprecher liest der Zuschauer selbst - er bleibt automatisch bis zum Satzende. " +
                                    "Da der Clip loopt, laufen viele Videos mehrfach durch, was die Watchtime nach oben zieht.",
                            "Kein Skript, keine Stimme, kein Timing: ein Clip, ein Textfeld, ein Trend-Sound. " +
                                    "In der Zeit für ein normales Motivations-Video baust du fünf davon.",
                            8,
                            List.of(
                                    "10 ruhige Loop-Clips von Pexels.com laden (Regen, Meer, Stadt bei Nacht)",
                                    "Pro Video einen starken Satz mittig als Text-Overlay setzen",
                                    "Trend-Sound drüberlegen, Video auf 8-12 Sekunden kürzen, posten"
                            )
                    )
            ),
            new Nische(
                    "Reddit-Storytime (vorgelesene Geschichten)",
                    List.of("reddit", "aita", "storytime", "vorgelesen", "text to speech", "geschichte vorgelesen"),
                    "Echte, emotionale Alltagskonflikte machen neugierig auf den Ausgang. Der Zuschauer will wissen, " +
                            "wer im Recht war - und will darüber urteilen.",
                    "Das Hintergrund-Gameplay hält den Blick auf dem Bildschirm, während die Stimme die Geschichte " +
                            "erzählt. Ergebnis: sehr hohe Watchtime. Zusätzlich lösen Streitfälle massenhaft " +
                            "Meinungs-Kommentare aus.",
                    "'Ich habe meiner besten Freundin die Hochzeit ruiniert - und ich würde es wieder tun.'",
                    35,
                    List.of(
                            "Kürze härter als das Vorbild: Steig mitten im Konflikt ein und lass die Vorgeschichte komplett weg",
                            "Schneide die Geschichte VOR der Auflösung ab und löse sie in Teil 2 auf - das bringt Zuschauer auf dein Profil",
                            "Frag am Ende konkret 'Wer war im Recht?' statt nur zu erzählen - das verdoppelt oft die Kommentare",
                            "Nutze ein Hintergrundvideo, das kaum jemand verwendet - Subway Surfers ist übersättigt und wirkt beliebig"
                    ),
                    List.of(
                            "Eigene, spezifische Story-Kategorie wählen statt gemischter Themen (z.B. nur Arbeit/Chef-Storys)",
                            "Geschichten in Cliffhanger-Teilen als Serie posten (Teil 1, Teil 2 ...)",
                            "Community eigene Geschichten einsenden lassen, statt nur Reddit zu nutzen"
                    ),
                    List.of(
                            "Passende Geschichte auf Reddit suchen (z.B. r/AmItheAsshole) - Regeln des Subreddits beachten",
                            "Text kürzen/anpassen, damit er in 30-90 Sekunden passt",
                            "Kostenlose TTS-Stimme erzeugen (CapCut TTS oder Google Text-to-Speech)",
                            "Gratis-Hintergrundgameplay besorgen, das rechtefrei nutzbar ist",
                            "In CapCut Story-Audio über das Hintergrundvideo legen",
                            "Automatische Untertitel aktivieren (erhöht Watchtime deutlich)",
                            "Am Ende bewusst einen Cliffhanger setzen, um Teil 2 anzukündigen"
                    ),
                    new Alternative(
                            "Dilemma-Fragen ('Würdest du?') über Gameplay",
                            "Eine einzige harte Entscheidungsfrage löst mehr Kommentare aus als eine ganze Geschichte - " +
                                    "und Kommentare sind das Signal, das kleine Kanäle am schnellsten wachsen lässt.",
                            "Zwei Sätze statt einer ganzen Geschichte: keine Recherche, keine Rechtefrage, kein langes " +
                                    "Skript. Du kannst 15 Videos in einer Stunde vorbereiten.",
                            10,
                            List.of(
                                    "20 Dilemma-Fragen aufschreiben ('100.000 Euro, aber du darfst nie wieder reisen - ja oder nein?')",
                                    "Frage als TTS + großes Text-Overlay über rechtefreies Gameplay legen",
                                    "Video bei 10-15 Sekunden halten und die Frage am Ende wiederholen"
                            )
                    )
            ),
            new Nische(
                    "Psychologie-Tricks",
                    List.of("psychologie", "psychology", "manipulation", "körpersprache", "dark psychology"),
                    "Wissen darüber, wie Menschen ticken, fühlt sich wie ein persönlicher Vorteil an. Der Zuschauer " +
                            "speichert das Video, weil er es 'demnächst mal anwenden' will.",
                    "Hohe Speicher- und Teilrate, weil Zuschauer solche Tricks an Freunde weiterschicken. " +
                            "Gleichzeitig entstehen viele Kommentare von Zweiflern, was die Reichweite zusätzlich antreibt.",
                    "'Dieser Trick lässt jeden Menschen dir sofort vertrauen.'",
                    30,
                    List.of(
                            "Zeig den Trick als Mini-Dialog statt ihn nur zu erklären - Anwendung schlägt Erklärung",
                            "Nenne die Studie oder das Buch dahinter: Das trauen sich die wenigsten Konkurrenten und es baut Vertrauen auf",
                            "Erkläre auch, wann der Trick NICHT funktioniert - solche ehrlichen Videos werden auffällig oft geteilt",
                            "Baue eine feste Serie mit Nummerierung auf ('Trick #14'), damit Zuschauer die früheren Teile suchen"
                    ),
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
                    ),
                    new Alternative(
                            "Mini-Psychotests ('Was siehst du zuerst?')",
                            "Der Zuschauer antwortet innerlich sofort und will seine Antwort in den Kommentaren bestätigt " +
                                    "sehen. Solche Videos erzeugen pro Aufruf mehr Kommentare als fast jedes andere Format.",
                            "Ein Bild und zwei Auflösungssätze - keine Recherche, kein Skript, keine Quellenprüfung.",
                            8,
                            List.of(
                                    "Ein mehrdeutiges Bild wählen (Gratis-Bilder bei Pixabay.com)",
                                    "Frage einblenden, 3 Sekunden Pause lassen, dann zwei kurze Deutungen zeigen",
                                    "Am Ende 'Schreib deine Antwort in die Kommentare' einblenden"
                            )
                    )
            ),
            new Nische(
                    "Luxus & Wealth",
                    List.of("luxus", "reich", "geld", "wealth", "money", "lifestyle"),
                    "Bilder von Reichtum lösen Sehnsucht und Vergleich aus. Der Zuschauer schaut sich das Leben an, " +
                            "das er gerne hätte - das funktioniert auch völlig ohne Gesicht.",
                    "Der Content ist visuell sofort verständlich und braucht keine Sprachkenntnisse, deshalb wird er " +
                            "oft auch international ausgespielt. Das Publikum ist riesig, die Konkurrenz aber ebenso.",
                    "'So sieht ein Tag als Millionär wirklich aus.'",
                    25,
                    List.of(
                            "Gib echten Nutzen statt nur Bilder: ein konkreter Spar- oder Investment-Gedanke pro Video schlägt reine Protzerei",
                            "Nutze Gegenüberstellungen ('mit 2.000 im Monat vs. mit 10.000') - Vergleiche halten Zuschauer bis zum Ende",
                            "Bleib glaubwürdig und behaupte nicht, es sei dein eigenes Leben - Zuschauer erkennen Stock-Material und kommentieren es negativ",
                            "Sprich eine realistische Zielgruppe an (Berufseinsteiger statt Millionäre) - dort ist die Bindung viel höher"
                    ),
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
                    ),
                    new Alternative(
                            "Preis-Raten ('Was kostet das?')",
                            "Raten aktiviert den Zuschauer sofort und die Auflösung am Ende erzwingt, dass er bis zum " +
                                    "Schluss bleibt. Falsche Schätzungen landen massenhaft in den Kommentaren.",
                            "Ein Clip, eine Zahl, eine Auflösung - kein Skript, keine Recherche außer dem Preis selbst.",
                            10,
                            List.of(
                                    "Gegenstand + echten Preis recherchieren (10 Stück auf einmal sammeln)",
                                    "Clip zeigen, Frage einblenden, 3 Sekunden Countdown, dann Preis groß auflösen",
                                    "Video bei 10-15 Sekunden halten und zum Raten in den Kommentaren auffordern"
                            )
                    )
            ),
            new Nische(
                    "Geschichte & History-Facts",
                    List.of("history", "historisch", "weltkrieg", "antike", "mittelalter", "geschichte der"),
                    "Wenig bekannte historische Momente wirken wie 'verschwiegenes Wissen'. Das Gefühl, etwas zu " +
                            "erfahren, was in der Schule nie vorkam, ist ein sehr starker Antrieb zum Weiterschauen.",
                    "Solche Videos werden häufig in Gruppenchats geteilt und lösen lange Diskussionen in den " +
                            "Kommentaren aus - beides Signale, die den Algorithmus stark antreiben.",
                    "'Das ist das dunkelste Kapitel, über das in der Schule nie gesprochen wird.'",
                    35,
                    List.of(
                            "Erzähl aus der Perspektive einer einzelnen Person statt aus der Vogelperspektive - Menschen binden stärker als Jahreszahlen",
                            "Nimm ein Ereignis, das alle zu kennen glauben, und zeig das unbekannte Detail daran",
                            "Baue eine feste Chronologie-Serie auf, damit Zuschauer den nächsten Teil erwarten",
                            "Nenne deine Quelle im Overlay - in dieser Nische gibt es viele Falschbehauptungen, Genauigkeit hebt dich klar ab"
                    ),
                    List.of(
                            "Eine enge Epoche/Region wählen statt 'random Geschichte' (z.B. nur Antikes Rom)",
                            "Geschichten als 'Was wäre, wenn'-Szenario erzählen statt reiner Fakten",
                            "Serie mit durchlaufender Chronologie aufbauen (z.B. jede Woche 1 Jahrzehnt)"
                    ),
                    List.of(
                            "Verlässliche Quelle recherchieren (Bücher, Dokumentationen, seriöse Wikipedia-Quellen)",
                            "Kurzes, spannend geschriebenes Skript mit Hook erstellen",
                            "Kostenlose TTS-Stimme mit dramatischem Ton wählen",
                            "Gratis historisches Material nutzen (gemeinfrei, z.B. Wikimedia Commons, Pexels)",
                            "In CapCut mit Ken-Burns-Effekt (langsames Zoomen auf Bilder) schneiden",
                            "Automatische Untertitel aktivieren und passenden dramatischen Trend-Sound wählen"
                    ),
                    new Alternative(
                            "Damals vs. Heute (zwei Bilder, ein Ort)",
                            "Der direkte Vorher-Nachher-Vergleich wird in einer Sekunde verstanden und löst sofort " +
                                    "Staunen aus. Solche Videos werden stark geteilt, ohne dass du etwas erzählen musst.",
                            "Zwei gemeinfreie Bilder und eine Jahreszahl statt einer recherchierten Geschichte. " +
                                    "Kein Skript, keine Stimme nötig.",
                            10,
                            List.of(
                                    "Historisches Bild (Wikimedia Commons, gemeinfrei) + aktuelles Bild desselben Orts suchen",
                                    "Beide Bilder mit Wisch-Übergang in CapCut gegenüberstellen, Jahreszahlen einblenden",
                                    "Ruhigen Trend-Sound drüberlegen, 10 Sekunden, fertig"
                            )
                    )
            ),
            new Nische(
                    "Top-Listen & Rankings",
                    List.of("top 5", "top 10", "liste", "ranking", "die besten", "top10", "top5"),
                    "Eine Liste gibt dem Gehirn eine klare Struktur und ein Versprechen: Platz 1 kommt noch. " +
                            "Dieses offene Ende hält den Zuschauer bis zur letzten Sekunde.",
                    "Der Countdown erzeugt hohe Completion-Rate, weil das Ende der Belohnungsmoment ist. " +
                            "Zusätzlich streiten Zuschauer in den Kommentaren über die Reihenfolge.",
                    "'Platz 5 wird dich überraschen - aber Platz 1 ist unfassbar.'",
                    30,
                    List.of(
                            "Kündige Platz 1 schon im Hook an ('Platz 1 hat mich echt schockiert') - das ist der Grund, warum jemand bleibt",
                            "Begründe jede Platzierung in einem Satz - reine Aufzählungen wirken beliebig und werden weggewischt",
                            "Wähle ein Ranking, bei dem Leute widersprechen wollen - Streit in den Kommentaren ist hier der Wachstumsmotor",
                            "Halte pro Platz maximal 5 Sekunden, sonst brechen Zuschauer vor Platz 1 ab"
                    ),
                    List.of(
                            "Extrem enges Listenthema wählen (nicht 'Top 10 Autos', sondern 'Top 5 Autos unter 10.000 Euro')",
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
                    ),
                    new Alternative(
                            "Dieses oder jenes ('Was nimmst du?')",
                            "Zwei Optionen statt fünf Plätze - der Zuschauer entscheidet sich in einer Sekunde und will " +
                                    "das kommentieren. Die Kommentarrate liegt meist deutlich über der von Top-Listen.",
                            "Statt fünf recherchierter Plätze mit fünf Clips brauchst du zwei Bilder und eine Frage.",
                            8,
                            List.of(
                                    "20 Entscheidungspaare aus deiner Nische aufschreiben",
                                    "Zwei Bilder nebeneinander in CapCut, Frage groß darüber",
                                    "8-12 Sekunden, Trend-Sound, Aufforderung zum Kommentieren einblenden"
                            )
                    )
            ),
            new Nische(
                    "ASMR & Satisfying",
                    List.of("asmr", "satisfying", "entspannend", "seife schneiden", "kinetic sand", "oddly satisfying"),
                    "Gleichmäßige Bewegungen und saubere Geräusche wirken beruhigend. Der Zuschauer schaut passiv " +
                            "weiter, ohne bewusst zu entscheiden - genau das erzeugt sehr lange Sehdauer.",
                    "Sprache spielt keine Rolle, deshalb wird der Content weltweit ausgespielt. Zuschauer sehen " +
                            "solche Videos oft mehrfach hintereinander, was den Algorithmus stark begünstigt.",
                    "Kein gesprochener Hook nötig - der erste visuelle Reiz in Sekunde 1 muss sofort wirken",
                    30,
                    List.of(
                            "Setz den befriedigendsten Moment an den Anfang, nicht ans Ende - die meisten Kanäle verschenken hier die erste Sekunde",
                            "Achte mehr auf den Ton als auf das Bild - sauberer Klang ist in dieser Nische der eigentliche Unterschied",
                            "Film in einer Naheinstellung ohne Hintergrundunruhe, damit das Bild sofort ruhig wirkt",
                            "Lass das Video am Ende nahtlos zum Anfang passen, damit es sich unbemerkt wiederholt"
                    ),
                    List.of(
                            "Eigenes, noch seltenes Material finden statt bekannte ASMR-Trends zu kopieren",
                            "Serie mit wiederkehrendem Objekt/Material aufbauen (Wiedererkennungswert)",
                            "Leichten Lern-Effekt einbauen (z.B. 'so wird X hergestellt') statt nur reinem Sound"
                    ),
                    List.of(
                            "Ruhige Umgebung und gutes Mikrofon (auch Handy-Mikro reicht oft) für sauberen Ton nutzen",
                            "Motiv/Material auswählen, das noch nicht überall zu sehen ist",
                            "In gleichmäßigem Tempo und naher Kameraeinstellung filmen (Handy reicht)",
                            "In CapCut nur minimal schneiden, Ton-Qualität priorisieren, Video nicht überladen",
                            "Kein Overlay-Text nötig, ggf. kurzer Titel am Anfang",
                            "Ruhigen oder passenden Trend-Sound leise unterlegen und regelmäßig posten"
                    ),
                    new Alternative(
                            "Aufräum- und Ordnungs-Clips (Restock/Cleaning)",
                            "Der Vorher-Nachher-Effekt liefert dieselbe Befriedigung wie klassisches ASMR, hat aber " +
                                    "zusätzlich ein klares Ziel - der Zuschauer bleibt, bis alles ordentlich ist.",
                            "Du brauchst keine Spezialmaterialien: Du filmst etwas, das du ohnehin machst " +
                                    "(Schrank einräumen, Schreibtisch sortieren, Kühlschrank auffüllen).",
                            15,
                            List.of(
                                    "Handy auf einen Stapel Bücher stellen, unordentliche Ecke ins Bild nehmen",
                                    "Ordnen und dabei durchgehend filmen, danach in CapCut auf 15 Sekunden raffen",
                                    "Vorher-Bild an den Anfang setzen, ruhigen Trend-Sound drüberlegen"
                            )
                    )
            ),
            new Nische(
                    "Horror & Gruselgeschichten",
                    List.of("horror", "gruselgeschichte", "creepy", "scary story", "gruselig"),
                    "Angst ist ein körperlicher Reiz, der Aufmerksamkeit erzwingt. Der Zuschauer bleibt aus " +
                            "Nervenkitzel bis zum Ende, selbst wenn ihm unwohl ist.",
                    "Gruselvideos erzeugen sehr viele Kommentare ('das ist fake', 'ich schlafe nicht mehr') und " +
                            "werden nachts überdurchschnittlich lange geschaut - beides treibt die Reichweite.",
                    "'Das ist mir wirklich passiert - und ich schlafe seitdem mit Licht.'",
                    35,
                    List.of(
                            "Beginne mit dem unheimlichsten Moment und erzähl erst danach, wie es dazu kam",
                            "Nutze Stille statt Dauermusik vor dem Höhepunkt - Stille wirkt bedrohlicher als jeder Soundeffekt",
                            "Verorte die Geschichte konkret (Ort, Uhrzeit, Alter) - Details machen sie glaubwürdiger als vage Erzählungen",
                            "Halte die Auflösung kurz und lass eine Frage offen, damit die Kommentare weiterdiskutieren"
                    ),
                    List.of(
                            "Enges Grusel-Sub-Genre wählen (z.B. nur wahre Begebenheiten, nur Wald/Camping-Storys)",
                            "Geschichten als mehrteilige Serie mit Cliffhanger erzählen",
                            "Zuschauer eigene Grusel-Erlebnisse einsenden lassen für authentischen Content"
                    ),
                    List.of(
                            "Kurze, spannend aufgebaute Gruselgeschichte schreiben oder recherchieren (Quellenregeln beachten)",
                            "Kostenlose dunkle/tiefe TTS-Stimme nutzen (CapCut TTS)",
                            "Dunkles, ruhiges Gratis-B-Roll (Wald, leere Straßen, Nebel) bei Pexels.com laden",
                            "In CapCut mit dunklem Filter und langsamen Schnitten arbeiten",
                            "Automatische Untertitel aktivieren, an Spannungspunkten kurz Stille/Soundeffekt setzen",
                            "Am Ende bewusst offenes Ende/Cliffhanger für Teil 2 lassen"
                    ),
                    new Alternative(
                            "Creepy Facts (3 kurze Grusel-Fakten statt einer Geschichte)",
                            "Der Gruseleffekt kommt sofort und dreimal pro Video statt einmal am Ende. Kurze " +
                                    "Grusel-Fakten werden häufiger zu Ende geschaut als lange Geschichten.",
                            "Keine Story-Rechte, kein Spannungsbogen, kein Cliffhanger-Timing - drei Sätze reichen.",
                            12,
                            List.of(
                                    "15 kurze Grusel-Fakten recherchieren (Tiefsee, Weltall, Medizin)",
                                    "Pro Video 3 Fakten, je ein dunkler Gratis-Clip von Pexels.com",
                                    "TTS drüber, Auto-Untertitel, 20 Sekunden, dunkler Filter"
                            )
                    )
            ),
            new Nische(
                    "Bedeutungen & Erklärungen (\"Was bedeutet ...?\")",
                    List.of("was bedeutet", "bedeutung", "erklärt", "erklärung", "slang",
                            "emoji", "traumdeutung", "wort"),
                    "Die Frage im Titel öffnet eine Wissenslücke, die der Zuschauer sofort schließen will. " +
                            "Er bleibt nicht, weil das Video unterhält, sondern weil die Antwort noch fehlt - " +
                            "das ist einer der zuverlässigsten Aufmerksamkeits-Auslöser überhaupt.",
                    "Dieser Content wird gesucht, nicht nur ausgespielt: Leute tippen solche Fragen direkt in " +
                            "die TikTok-Suche. Solche Videos sammeln deshalb über Monate weiter Aufrufe, lange " +
                            "nachdem sie gepostet wurden. Zusätzlich fragen Zuschauer in den Kommentaren nach dem " +
                            "nächsten Wort - das erzeugt Kommentare und liefert gleichzeitig neue Themen.",
                    "'Wenn dir jemand [X] schreibt, meint er in Wirklichkeit das.'",
                    15,
                    List.of(
                            "Häng nach der Antwort noch ein Beispiel oder eine Ausnahme dran - sonst ist das Video "
                                    + "nach zwei Sekunden inhaltlich vorbei und die Watchtime bricht genau dort ein",
                            "Schreib den Begriff groß ins Bild, nicht nur in die Tonspur - ein großer Teil schaut ohne Ton",
                            "Nimm Begriffe, die wirklich gesucht werden: Tipp den Anfang in die TikTok-Suchleiste und "
                                    + "nutze die Vorschläge, die dir angezeigt werden",
                            "Beantworte Wörter aus deinen eigenen Kommentaren und sag das im Video - das bringt "
                                    + "Zuschauer dazu, weitere Wörter zu fragen, und macht aus Zuschauern Stammpublikum"
                    ),
                    List.of(
                            "Nur ein Themenfeld statt alles gemischt (nur Jugendslang, nur Emojis, nur Träume, nur Namen)",
                            "Umgekehrte Variante: Begriffe, die fast alle falsch verwenden",
                            "Feste Nummerierung ('Wort #47'), damit Zuschauer auf dem Profil die alten Teile suchen"
                    ),
                    List.of(
                            "Ein Themenfeld festlegen und dabei bleiben",
                            "20 Begriffe sammeln, die laut TikTok-Suchvorschlägen wirklich gesucht werden",
                            "Skript in vier Teilen: Frage - Antwort nach 2 Sekunden - Beispielsatz - Ausnahme oder Zusatz",
                            "Kostenlose TTS-Stimme (CapCut) oder eigene Stimme aufnehmen",
                            "Begriff groß als Text-Overlay auf ruhigem Hintergrund zeigen",
                            "CapCut Auto-Untertitel aktivieren, Video auf 10-20 Sekunden halten",
                            "Am Ende fragen, welches Wort als Nächstes erklärt werden soll"
                    ),
                    new Alternative(
                            "Emoji-Bedeutungen",
                            "Emojis benutzt jeder täglich und die Suchnachfrage ist noch höher als bei Wörtern. " +
                                    "Das Video wird außerdem ohne Ton verstanden, was die Completion-Rate anhebt.",
                            "Du brauchst kein Bildmaterial: Das Emoji selbst füllt den Bildschirm. " +
                                    "Ein Emoji, ein Satz, fertig.",
                            6,
                            List.of(
                                    "20 häufig genutzte Emojis auflisten",
                                    "Emoji riesig auf einfarbigem Hintergrund, Frage als Overlay darüber",
                                    "2 Sekunden Pause zum Mitraten, dann Bedeutung einblenden - insgesamt 8-10 Sekunden"
                            )
                    )
            )
    );

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8);

        System.out.println("=================================================");
        System.out.println("   TikTok Faceless-Analyse (kostenlos)");
        System.out.println("=================================================");

        boolean laeuft = true;
        while (laeuft) {
            System.out.println("\nWas möchtest du analysieren?");
            System.out.println("  1) Fremden Kanal analysieren (Nische, Twist, Nachbau-Anleitung)");
            System.out.println("  2) Eigenes Video analysieren (warum viral oder warum wenig Aufrufe)");
            System.out.println("  3) Beenden");
            System.out.print("Auswahl: ");

            switch (scanner.nextLine().trim()) {
                case "1" -> analysiereKanal(scanner);
                case "2" -> VideoPerformanceAnalyse.starte(scanner);
                case "3" -> laeuft = false;
                default -> System.out.println("Bitte 1, 2 oder 3 eingeben.");
            }
        }

        System.out.println("\nViel Erfolg mit deinem Kanal!");
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

        bericht.append("Erkannte Nische: ").append(nische.name()).append("\n");
        bericht.append("Aufwand pro Video: ca. ").append(nische.aufwandMinuten()).append(" Minuten\n\n");

        bericht.append("--- WARUM DIESE NISCHE FUNKTIONIERT ---\n\n");
        bericht.append("Beim Zuschauer:\n").append(nische.psychologie()).append("\n\n");
        bericht.append("Beim Algorithmus:\n").append(nische.algorithmus()).append("\n\n");
        bericht.append("Typische Hook-Formel:\n").append(nische.hookFormel()).append("\n\n");

        bericht.append("--- EINSCHÄTZUNG DER KENNZAHLEN ---\n\n");
        bericht.append("- Videolänge (").append(videoLaenge).append("s): ")
                .append(bewerteVideolaenge(videoLaenge)).append("\n");
        bericht.append("- Postings pro Woche (").append(postingsProWoche).append("): ")
                .append(bewertePostingFrequenz(postingsProWoche)).append("\n");
        bericht.append("- Durchschnittliche Views: ").append(bewerteViews(durchschnittsViews)).append("\n\n");

        bericht.append("--- SO MACHST DU ES BESSER ALS DER KANAL ---\n\n");
        nummeriere(bericht, nische.besserMachen());
        bericht.append("\n");

        bericht.append("--- TWIST-IDEEN (gleiche Formel, eigener Winkel) ---\n\n");
        nummeriere(bericht, nische.twistIdeen());
        bericht.append("\n");

        Alternative alt = nische.alternative();
        bericht.append("--- EINFACHERE ALTERNATIVE MIT GLEICHEM POTENZIAL ---\n\n");
        bericht.append("Nische: ").append(alt.name()).append("\n");
        bericht.append("Aufwand: ca. ").append(alt.aufwandMinuten()).append(" Minuten pro Video (statt ")
                .append(nische.aufwandMinuten()).append(" Minuten)\n");
        bericht.append(vergleicheAufwand(nische.aufwandMinuten(), alt.aufwandMinuten())).append("\n\n");
        bericht.append("Warum sie genauso gut läuft:\n").append(alt.warumGenausoGut()).append("\n\n");
        bericht.append("Warum sie einfacher ist:\n").append(alt.warumEinfacher()).append("\n\n");
        bericht.append("Schnellstart:\n");
        nummeriere(bericht, alt.schnellstart());
        bericht.append("\n");

        bericht.append("--- SCHRITT FÜR SCHRITT NACHBAUEN (so gut wie kostenlos) ---\n\n");
        nummeriere(bericht, nische.schritte());

        return bericht.toString();
    }

    private static void nummeriere(StringBuilder ziel, List<String> punkte) {
        int nummer = 1;
        for (String punkt : punkte) {
            ziel.append(nummer++).append(". ").append(punkt).append("\n");
        }
    }

    private static String vergleicheAufwand(int original, int alternative) {
        if (alternative >= original) {
            return "Der Aufwand ist vergleichbar - der Vorteil liegt hier im Format, nicht in der Zeit.";
        }
        int gespart = original - alternative;
        int videosProStunde = 60 / alternative;
        return "Du sparst rund " + gespart + " Minuten pro Video und schaffst damit etwa "
                + videosProStunde + " Videos in einer Stunde.";
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

    static void speichereBericht(String kanalname, String bericht) {
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
