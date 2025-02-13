import java.util.Scanner;
public class Party {
    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        int gaste;
        boolean weiter = true;
        System.out.println("Wie viele Gäste sind eingeladen?");
        gaste = scan.nextInt();

        while (weiter) {
           System.out.println("anmelden(1), abmelden(2), beenden(3)");
           int value = scan.nextInt();
           if (value == 1) {
               System.out.println("Wie viele Gäste kommen dazu?");
                gaste += scan.nextInt();
           } else if (value == 2) {
               System.out.println("Wie viele Gäste gehen?");
               gaste -= scan.nextInt();
           } else if (value == 3) {
                weiter = false;
               System.out.println("Es sind " + gaste + " Gäste eingeladen.");
           }
        }

    }
}
