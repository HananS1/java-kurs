import java.util.Scanner;

public class Test {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int score = 0;

        System.out.println("Willkommen zum Sexual Orientation Test!");
        System.out.println("Beantworten Sie die folgenden Fragen mit 'Ja' oder 'Nein'.");

        // Frage 1
        System.out.println("Frage 1: Finden Sie Menschen des gleichen Geschlechts attraktiv?");
        String antwort1 = scanner.nextLine();
        if (antwort1.equalsIgnoreCase("Ja")) {
            score++;
        }

        // Frage 2
        System.out.println("Frage 2: Finden Sie Menschen des anderen Geschlechts attraktiv?");
        String antwort2 = scanner.nextLine();
        if (antwort2.equalsIgnoreCase("Ja")) {
            score--;
        }

        // Frage 3
        System.out.println("Frage 3: Fühlen Sie sich in Beziehungen mit Menschen des gleichen Geschlechts wohler?");
        String antwort3 = scanner.nextLine();
        if (antwort3.equalsIgnoreCase("Ja")) {
            score++;
        }

        // Frage 4
        System.out.println("Frage 4: Fühlen Sie sich in Beziehungen mit Menschen des anderen Geschlechts wohler?");
        String antwort4 = scanner.nextLine();
        if (antwort4.equalsIgnoreCase("Ja")) {
            score--;
        }

        // Humorvolle Frage 1
        System.out.println("Frage 5: Glauben Sie, dass Einhörner echt sind?");
        String antwort5 = scanner.nextLine();
        if (antwort5.equalsIgnoreCase("Ja")) {
            System.out.println("Interessant! Aber lassen Sie uns zum Test zurückkehren.");
        }

        // Kritische Frage 1
        System.out.println("Frage 6: Glauben Sie an gleiche Rechte für alle sexuellen Orientierungen?");
        String antwort6 = scanner.nextLine();
        if (antwort6.equalsIgnoreCase("Ja")) {
            score++;
        }

        // Humorvolle Frage 2
        System.out.println("Frage 7: Gehört Ananas auf Pizza?");
        String antwort7 = scanner.nextLine();
        if (antwort7.equalsIgnoreCase("Ja")) {
            System.out.println("Das ist eine kontroverse Meinung!");
        }

        // Kritische Frage 2
        System.out.println("Frage 8: Unterstützen Sie die gleichgeschlechtliche Ehe?");
        String antwort8 = scanner.nextLine();
        if (antwort8.equalsIgnoreCase("Ja")) {
            score++;
        }

        // Ergebnis
        if (score > 0) {
            System.out.println("Basierend auf Ihren Antworten könnten Sie homosexuell sein.");
        } else if (score < 0) {
            System.out.println("Basierend auf Ihren Antworten könnten Sie heterosexuell sein.");
        } else {
            System.out.println("Basierend auf Ihren Antworten könnten Sie bisexuell oder unsicher sein.");
        }
    }
}