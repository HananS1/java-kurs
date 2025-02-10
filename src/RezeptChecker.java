public class RezeptChecker {
    public static void main(String[] args) {
        //Menge an Zutaten:
        int menge_zucker = 110;
        boolean rapsoel_vorhanden = false;
        boolean sonnenblumenoel_vorhanden = true;
        int menge_mehl = 400;

        //Prüfung des Rezepts:
        if (menge_zucker >= 50 && menge_zucker <= 100) {
            System.out.println("Richtige Menge an Zucker vorhanden");
        } else {
            System.out.println("Zu viel oder zu wenig Mehl"); //Wie kann man hier die einzelnen Fälle prüfen?
        }

        if (menge_mehl >= 200 && menge_mehl <= 400) {
            System.out.println("Richtige Menge an Mehl vorhanden");
        } else {
            System.out.println("Zu viel oder zu wenig Mehl");
        }

        if (rapsoel_vorhanden || sonnenblumenoel_vorhanden) {
            System.out.println("Öl vorhanden");
        } else {
            System.out.println("Kein Öl mehr da!");
        }

    }
}
